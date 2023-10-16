import ast
import json
from datetime import datetime, timedelta

import requests
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.utils import timezone
from requests_oauthlib import OAuth1Session
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from core.models import Project, UserProfile
from core.utils import IsWhitelisted, StandardResponse, get_openai_response
from twitter.constants import (
    CALLBACK_URI,
    CONSUMER_KEY,
    CONSUMER_SECRET,
    DAILY_TWEET_LIMIT,
    TWITTER_ACCESS_TOKEN_URL,
    TWITTER_API_ENDPOINT,
    TWITTER_REQUEST_TOKEN_URL,
)
from twitter.models import Tweets, TwitterAccount
from twitter.serializers import (
    FetchTweetRequestSerializer,
    PostTweetRequestSerializer,
    TweetSerializer,
)

bearer_token = "AAAAAAAAAAAAAAAAAAAAAGBtpAEAAAAAmbcFbMA8obK9WjTB6RlyOLOUUeU%3D5vJU4bgltWJzN0f8uztn5WWSpBd1dGRYPDbePw0heobKcuVyap"

User = get_user_model()


def bearer_oauth(r):
    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2RecentSearchPython"
    return r


class CheckTwitterView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsWhitelisted]

    def get(self, request, *args, **kwargs):
        user = User.objects.get(id=request.user.id)
        twtr_acc = TwitterAccount.objects.filter(user=user)

        if twtr_acc.exists():
            acc = twtr_acc[0]
            return StandardResponse(
                data={
                    "username": acc.username,
                    "twitter_id": acc.twitter_id,
                },
                errors=None,
                status_code=status.HTTP_200_OK,
            )

        return StandardResponse(
            data=None,
            errors=None,
            status_code=status.HTTP_200_OK,
        )


class ProjectTweetsListView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsWhitelisted]

    def get(self, request, project_id, format=None):
        tweet_state = request.GET.get("state", None)

        tweets = Tweets.objects.filter(project__id=project_id).order_by("id")
        if tweet_state:
            tweets = Tweets.objects.filter(
                project__id=project_id, state=tweet_state
            ).order_by("id")

        paginator = PageNumberPagination()
        paginated_tweets = paginator.paginate_queryset(tweets, request)
        serializer = TweetSerializer(paginated_tweets, many=True)

        response_data = {
            "count": paginator.page.paginator.count,
            "next": paginator.get_next_link(),
            "previous": paginator.get_previous_link(),
            "results": serializer.data,
        }

        return StandardResponse(
            data=response_data,
            errors=None,
            status_code=status.HTTP_200_OK,
        )


class FetchTweetsView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsWhitelisted]

    def post(self, request, *args, **kwargs):
        serializer = FetchTweetRequestSerializer(
            data=request.data, context={"request": request}
        )
        if not serializer.is_valid():
            return StandardResponse(
                data=None,
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        self.user_profile = UserProfile.objects.get(user=request.user)
        if self.user_profile.tweets_left <= 0 or request.user.is_active is False:
            return StandardResponse(
                data=None,
                errors={"message": "limit exhausted"},
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        self.project = Project.objects.get(
            id=serializer.validated_data["project_id"], user=request.user
        )

        self.keywords = self.project.keywords
        twtr_query = self.build_twitter_query(
            keywords=json.loads(self.project.keywords),
            max_results=10,
            screen_name=request.user.username,
        )

        json_response = self.connect_to_endpoint(
            url=TWITTER_API_ENDPOINT, params=twtr_query
        )

        clean_tweets, total_counts = self.process_tweets_and_responses(json_response)
        if not clean_tweets:
            return StandardResponse(
                data=None,
                errors={"message": "limit exhausted"},
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
        self.create_tweets(tweets=clean_tweets, total_count=total_counts)
        query = Tweets.objects.filter(user=request.user, project=self.project).order_by(
            "-created_at"
        )
        paginator = PageNumberPagination()
        paginated_tweets = paginator.paginate_queryset(query, request)
        serialized_tweets = TweetSerializer(paginated_tweets, many=True)
        response_data = {
            "count": paginator.page.paginator.count,
            "next": paginator.get_next_link(),
            "previous": paginator.get_previous_link(),
            "results": serialized_tweets.data,
        }

        return StandardResponse(
            data=response_data,
            errors=None,
            status_code=status.HTTP_200_OK,
        )

    def create_tweets(self, tweets, total_count):
        for tweet in tweets:
            Tweets.objects.create(
                user=self.request.user,
                author_id=tweet["author_id"],
                tweet_id=tweet["id"],
                project=self.project,
                tweet_content=tweet["text"],
                ai_response=tweet["response"],
                misc_data={},
                state="FETCHED",
            )
            self.user_profile.tweets_left -= total_count
            self.user_profile.save()

    def connect_to_endpoint(self, url, params):
        response = requests.get(url, auth=bearer_oauth, params=params)
        if response.status_code != 200:
            raise Exception(f"Error: {response.status_code}, {response.text}")
        return response.json()

    def build_twitter_query(self, keywords, max_results, screen_name):
        keywords = list(map(lambda x: f'"{x}"', keywords))
        query_str = f'({" OR ".join(keywords)})'
        query_str += f" -is:retweet -is:reply lang:en -from:{screen_name}"

        query_params = {
            "query": query_str,
            "tweet.fields": "author_id,created_at",
            "user.fields": "name",
            "max_results": str(max_results),
        }

        return query_params

    def process_tweets_and_responses(self, json_response):
        clean_tweets = []
        total_counts = 0
        tweet_count_2 = 0

        next_token = json_response["meta"].get("next_token", None)
        tweets = json_response.get("data", [])
        tweet_count_1 = len(tweets)

        processed_tweets = set()
        processed_responses = set()
        min_relevant_responses = 5
        relevant_responses_count = 0
        twitter_request_count = 0

        while relevant_responses_count < min_relevant_responses:
            twitter_request_count += 1
            if twitter_request_count > 5:
                break

            for tweet in tweets:
                tweet_text = tweet.get("text", "")
                if tweet_text in processed_tweets:
                    continue
                openai_response = get_openai_response(
                    tweet_text=tweet_text,
                    soup_text=self.project.soup_text,
                    url=self.project.url,
                    keywords=self.project.keywords,
                    rules=self.project.ai_rules if self.project.ai_rules else "",
                )

                if (
                    "reply_text" in openai_response
                    and openai_response["reply_text"].strip()
                ):
                    if openai_response["reply_text"] in processed_responses:
                        continue

                    processed_tweets.add(tweet_text)
                    processed_responses.add(openai_response["reply_text"])
                    tweet["response"] = openai_response["reply_text"]
                    tweet["approved"] = "false"
                    tweet["posted"] = "false"
                    clean_tweets.append(tweet)

                    relevant_responses_count += 1

            if relevant_responses_count >= min_relevant_responses:
                break

        total_counts = tweet_count_1 + tweet_count_2
        return clean_tweets, total_counts


class PostTweetView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsWhitelisted]

    def post(self, request, *args, **kwargs):
        serializer = PostTweetRequestSerializer(
            data=request.data, context={"request": request}
        )
        if not serializer.is_valid():
            return StandardResponse(
                data=None,
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        if not request.user.is_active:
            return StandardResponse(
                data=None,
                errors={"message": "limit exhausted"},
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        if not self.check_daily_tweet_limit():
            return StandardResponse(
                data=None,
                errors={
                    "message": "Daily tweet limit exceeded, only 100 tweets allowed per day"
                },
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        self.tweet = Tweets.objects.get(id=serializer.validated_data["tweet_id"])

        tweet_published = self.publish_tweet()
        if not tweet_published:
            return StandardResponse(
                data=None,
                errors={
                    "message": "failed to post tweet, check your connected Twitter account"
                },
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        return StandardResponse(
            data={"tweet_id": self.tweet.tweet_id},
            errors=None,
            status_code=status.HTTP_201_CREATED,
        )

    def check_daily_tweet_limit(self) -> bool:
        daily_tweet_limit = DAILY_TWEET_LIMIT

        user = self.request.user
        today_start = timezone.make_aware(
            datetime.combine(datetime.today(), datetime.min.time())
        )
        today_end = today_start + timedelta(days=1)

        # Check the user's tweet count for today
        todays_tweet_count = Tweets.objects.filter(
            user=user,
            created_at__gte=today_start,
            created_at__lt=today_end,
            state="POSTED",
        ).count()
        if todays_tweet_count >= daily_tweet_limit:
            return False
        return True

    def publish_tweet(self) -> bool:
        try:
            twtr_acc = TwitterAccount.objects.get(user=self.request.user)
        except TwitterAccount.DoesNotExist:
            return False
        oAuth = OAuth1Session(
            CONSUMER_KEY,
            client_secret=CONSUMER_SECRET,
            resource_owner_key=twtr_acc.access_token,
            resource_owner_secret=twtr_acc.oauth_token_secret,
        )
        payload = {
            "text": self.tweet.ai_response,
            "reply": {"in_reply_to_tweet_id": self.tweet.tweet_id},
        }
        response = oAuth.post(
            "https://api.twitter.com/2/tweets",
            json=payload,
        )
        if response.status_code != 201:
            return False

        self.tweet.tweet_id = response.json()["data"]["id"]
        self.tweet.state = "POSTED"
        self.tweet.save()
        return True


class TweetDetailView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsWhitelisted]

    def get(self, request, pk, format=None):
        tweet = get_object_or_404(Tweets, pk=pk)
        serializer = TweetSerializer(tweet)
        return StandardResponse(
            data=serializer.data,
            errors=None,
            status_code=status.HTTP_200_OK,
        )

    def put(self, request, pk, format=None):
        tweet = get_object_or_404(Tweets, pk=pk)
        serializer = TweetSerializer(tweet, data=request.data, partial=True)
        if not serializer.is_valid():
            return StandardResponse(
                data=None,
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        serializer.save()
        return StandardResponse(
            data=serializer.data,
            errors=None,
            status_code=status.HTTP_200_OK,
        )

    def delete(self, request, pk, format=None):
        tweet = get_object_or_404(Tweets, pk=pk)
        tweet.delete()
        return StandardResponse(
            data=None,
            errors=None,
            status_code=status.HTTP_204_NO_CONTENT,
        )


class RequestOAuthView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsWhitelisted]

    def get(self, request, *args, **kwargs):
        oAuth = OAuth1Session(
            client_key=CONSUMER_KEY,
            client_secret=CONSUMER_SECRET,
            callback_uri=CALLBACK_URI,
        )
        try:
            response = oAuth.fetch_request_token(TWITTER_REQUEST_TOKEN_URL)
        except requests.exceptions.RequestException as e:
            return StandardResponse(
                data=None,
                errors={"message": str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        oauth_token = response.get("oauth_token")
        oauth_callback_confirmed = response.get("oauth_callback_confirmed")

        if oauth_callback_confirmed != "true":
            return StandardResponse(
                data=None,
                errors={"message": "OAuth callback not confirmed by Twitter."},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        twtr_acc, created = TwitterAccount.objects.get_or_create(user=request.user)
        twtr_acc.oauth_token = oauth_token
        twtr_acc.save()

        return StandardResponse(
            data={
                "oauth_token": oauth_token,
                "internal_twitter_account_id": twtr_acc.id,
            },
            errors=None,
            status_code=status.HTTP_200_OK,
        )


class AccessTokenView(APIView):
    def get(self, request, *args, **kwargs):
        oauth_token = self.request.query_params.get("oauth_token")
        oauth_verifier = self.request.query_params.get("oauth_verifier")
        oAuth = OAuth1Session(
            client_key=CONSUMER_KEY,
            client_secret=CONSUMER_SECRET,
            resource_owner_key=oauth_token,
            verifier=oauth_verifier,
        )
        try:
            response = oAuth.fetch_access_token(TWITTER_ACCESS_TOKEN_URL)
        except requests.exceptions.RequestException as e:
            return StandardResponse(
                data=None,
                errors={"message": str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        access_token = response["oauth_token"]
        screen_name = response["screen_name"]
        access_token_secret = response["oauth_token_secret"]
        twitter_id = response["user_id"]
        twtr_account = self.get_twtr_acc(
            screen_name, access_token, oauth_token, access_token_secret, twitter_id
        )
        if twtr_account is None:
            return StandardResponse(
                data=None,
                errors={
                    "message": "Could not find Twitter account with the given oauth_token"
                },
                status_code=status.HTTP_404_NOT_FOUND,
            )
        redirect_url = f"https://engagex.bitbaza.io/dashboard/profile?oauth_token={oauth_token}&oauth_verifier={oauth_verifier}"
        return redirect(redirect_url)

    def get_twtr_acc(
        self, screen_name, access_token, oauth_token, access_token_secret, twitter_id
    ):
        try:
            twtr_acc = TwitterAccount.objects.get(oauth_token=oauth_token)
        except TwitterAccount.DoesNotExist:
            return None
        twtr_acc.username = screen_name
        twtr_acc.access_token = access_token
        twtr_acc.oauth_token_secret = access_token_secret
        twtr_acc.twitter_id = twitter_id
        twtr_acc.save()
        return twtr_acc


class TwitterAccountDelete(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsWhitelisted]

    def delete(self, request):
        try:
            user = User.objects.get(id=request.user.id)
            twitter_account = TwitterAccount.objects.get(user=user)
            twitter_account.delete()
            return StandardResponse(
                data={"message": "Twitter account deleted"},
                errors=None,
                status_code=status.HTTP_204_NO_CONTENT,
            )
        except TwitterAccount.DoesNotExist:
            return StandardResponse(
                data=None,
                errors={"message": "Twitter account not found"},
                status_code=status.HTTP_400_BAD_REQUEST,
            )

import json

import requests
from django.contrib.auth import get_user_model
from requests_oauthlib import OAuth1Session
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import Project, UserProfile
from core.utils import get_openai_response
from twitter.constants import (
    ACCESS_TOKEN,
    ACCESS_TOKEN_SECRET,
    CALLBACK_URI,
    CONSUMER_KEY,
    CONSUMER_SECRET,
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


class FetchTweetsView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = FetchTweetRequestSerializer(
            data=request.data, context={"request": request}
        )
        if not serializer.is_valid():
            return Response({"message": "Invalid data.", "errors": serializer.errors})

        self.project = Project.objects.get(
            id=serializer.validated_data["project_id"], user=request.user
        )
        self.user_profile = UserProfile.objects.get(user=request.user)
        self.keywords = self.project.keywords

        if self.user_profile.tweets_left <= 0 or request.user.is_active is False:
            return Response(
                {"data": {"error": "limit exhausted"}},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        twtr_query = self.build_twitter_query(
            keywords=self.project.keywords,
            max_results=10,
            screen_name=request.user.username,
        )

        json_response = self.connect_to_endpoint(
            url=TWITTER_API_ENDPOINT, params=twtr_query
        )

        clean_tweets, total_counts = self.process_tweets_and_responses(json_response)
        if not clean_tweets:
            return Response(
                {"message": "All tweets had empty OpenAI responses."},
                status=status.HTTP_200_OK,
            )
        self.create_tweets(tweets=clean_tweets, total_count=total_counts)
        query = Tweets.objects.filter(user=request.user, project=self.project)
        serialized_tweets = TweetSerializer(query, many=True)
        return Response(serialized_tweets.data, status=status.HTTP_200_OK)

    def create_tweets(self, tweets, total_count):
        for tweet in tweets:
            Tweets.objects.create(
                user=self.request.user,
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
        keywords = [
            "web3 database",
            "decentralized database",
            "zero knowledge proofs",
            "blockchain attributes",
            "database speed & privacy",
            "data transparency",
            "data privacy",
            "data verifiability",
            "firestore SDK",
            "wallet authentication",
        ]
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
                    rules="",
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
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = PostTweetRequestSerializer(
            data=request.data, context={"request": request}
        )
        if not serializer.is_valid():
            return Response(
                {"message": "Invalid data.", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not request.user.is_active:
            return Response(
                {"data": {"error": "limit exhausted"}},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        self.tweet = Tweets.objects.get(id=serializer.validated_data["tweet_id"])

        tweet_published = self.publish_tweet()
        if not tweet_published:
            return Response(
                {"message": "failed to post tweet"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        return Response({"message": "Tweet posted successfully."})

    def publish_tweet(self) -> bool:
        oAuth = OAuth1Session(
            CONSUMER_KEY,
            client_secret=CONSUMER_SECRET,
            resource_owner_key=ACCESS_TOKEN,
            resource_owner_secret=ACCESS_TOKEN_SECRET,
        )
        response = oAuth.post(
            "https://api.twitter.com/2/tweets",
            json=json.dumps(self.tweet.ai_response),
        )
        if response.status_code != 201:
            return False

        self.tweet.state = "POSTED"
        self.tweet.save()
        return True


class RequestOAuthView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        oAuth = OAuth1Session(
            client_key=CONSUMER_KEY,
            client_secret=CONSUMER_SECRET,
            callback_uri=CALLBACK_URI,
        )
        response = oAuth.fetch_request_token(TWITTER_REQUEST_TOKEN_URL)
        if not response:
            return Response(
                {"message": "Could not fetch request token."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        oauth_token = response.get("oauth_token")
        oauth_callback_confirmed = response.get("oauth_callback_confirmed")
        return Response(
            {
                "oauth_token": oauth_token,
                "oauth_callback_confirmed": oauth_callback_confirmed,
            }
        )


class AccessTokenView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        oauth_token = self.request.query_params.get("oauth_token")
        oauth_verifier = self.request.query_params.get("oauth_verifier")
        oAuth = OAuth1Session(
            client_key=CONSUMER_KEY,
            client_secret=CONSUMER_SECRET,
            resource_owner_key=oauth_token,
            verifier=oauth_verifier,
        )
        response = oAuth.fetch_access_token(TWITTER_ACCESS_TOKEN_URL)
        if not response:
            return Response(
                {"data": "Could not fetch access token."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        access_token = response["oauth_token"]
        screen_name = response["screen_name"]
        access_token_secret = response["oauth_token_secret"]
        twitter_id = response["user_id"]
        twtr_account = self.get_or_create_twtr_acc(
            screen_name, access_token, access_token_secret, twitter_id
        )

        return Response(
            {
                "data": {
                    "username": twtr_account.username,
                    "twitter_id": twtr_account.twitter_id,
                }
            },
            status=status.HTTP_200_OK,
        )

    def get_or_create_twtr_acc(
        self, screen_name, access_token, access_token_secret, twitter_id
    ):
        try:
            twtr_acc = TwitterAccount.objects.get(
                username=screen_name, user=self.request.user
            )
        except TwitterAccount.DoesNotExist:
            twtr_acc = TwitterAccount.objects.create(
                username=screen_name,
                access_token=access_token,
                oauth_token_secret=access_token_secret,
                twitter_id=twitter_id,
                user=self.request.user,
            )
        return twtr_acc

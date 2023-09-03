import json

import requests
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import Project, UserProfile
from core.utils import get_openai_response
from twitter.constants import TWITTER_API_ENDPOINT
from twitter.models import Tweets
from twitter.serializers import FetchTweetRequestSerializer, TweetSerializer

bearer_token = "AAAAAAAAAAAAAAAAAAAAAGBtpAEAAAAAmbcFbMA8obK9WjTB6RlyOLOUUeU%3D5vJU4bgltWJzN0f8uztn5WWSpBd1dGRYPDbePw0heobKcuVyap"

User = get_user_model()


def bearer_oauth(r):
    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2RecentSearchPython"
    return r


class FetchTweetsView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = FetchTweetRequestSerializer(data=request.data)
        if serializer.is_valid():
            self.project = Project.objects.get(
                id=serializer.validated_data["project_id"]
            )
            self.keywords = self.project.keywords

            request.user = User.objects.get(id=1)

            # Assuming that UserProfile model has a one-to-one relationship with User

            user_profile = UserProfile.objects.get(user=request.user)
            kws = '["web3 database", "decentralized database", "zero knowledge proofs", "blockchain attributes", "data transparency", "data privacy", "data verifiability", "developer-friendly interface", "wallet authentication", "database encryption"]'

            if user_profile.tweets_left > 0 and request.user.is_active:
                twtr_query = self.build_twitter_query(
                    keywords=kws,
                    max_results=10,
                    screen_name=request.user.username,
                )
                json_response = self.connect_to_endpoint(
                    url=TWITTER_API_ENDPOINT, params=twtr_query
                )

                clean_tweets, total_counts = self.process_tweets_and_responses(
                    json_response
                )
                if clean_tweets:
                    for tweet in clean_tweets:
                        Tweets.objects.create(
                            user=request.user,
                            project=self.project,
                            tweet_content=tweet["text"],
                            ai_response=tweet["response"],
                            misc_data={},
                            state="FETCHED",
                        )
                        user_profile.tweets_left -= total_counts
                        user_profile.save()
                    query = Tweets.objects.filter(
                        user=request.user, project=self.project
                    )
                    serialized_tweets = TweetSerializer(query, many=True)
                    return Response(serialized_tweets.data, status=status.HTTP_200_OK)
                else:
                    return Response(
                        {"message": "All tweets had empty OpenAI responses."}
                    )
            else:
                return Response(
                    {"data": {"error": "limit exhausted"}},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
        else:
            return Response({"message": "Invalid data.", "errors": serializer.errors})

    def connect_to_endpoint(self, url, params):
        # Placeholder for your actual authentication method
        response = requests.get(url, auth=bearer_oauth, params=params)
        if response.status_code != 200:
            raise Exception(f"Error: {response.status_code}, {response.text}")
        return response.json()

    def build_twitter_query(self, keywords, max_results, screen_name):
        keywords = list(map(lambda x: f'"{x}"', keywords))
        query_str = f'({" OR ".join(keywords)})'
        query_str += f" -is:retweet -is:reply lang:en -from:{screen_name}"

        query_params = {
            "query": "python",
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

import json

import openai
import requests
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from core.constants import OPEN_AI_APIKEY
from core.models import Project
from core.utils import IsWhitelisted, StandardResponse
from lunarcrush.serializers import GetFeedsSerializer, GetInfluencersSerializer
from lunarcrush.utils import get_lunarcrush_coins_infulencers, get_lunarcrush_coins_feeds, get_openai_response
from twitter.models import Tweets
from twitter.serializers import TweetSerializer

User = get_user_model()


class GetFeedsView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsWhitelisted]

    def post(self, request, *args, **kwargs):
        serializer = GetFeedsSerializer(
            data=request.data, context={"request": request}
        )
        if not serializer.is_valid():
            return StandardResponse(
                data=None,
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        coin_symbol = serializer.validated_data["coin_symbol"]
        response = get_lunarcrush_coins_feeds(coin_symbol)
        return StandardResponse(
            data={"feeds": response.json()['data']}, errors=None, status_code=status.HTTP_200_OK
        )


class GetInfluencersView(APIView):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated, IsWhitelisted]

    def post(self, request, *args, **kwargs):
        serializer = GetInfluencersSerializer(
            data=request.data, context={"request": request}
        )
        if not serializer.is_valid():
            return StandardResponse(
                data=None,
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        coin_symbol = serializer.validated_data["coin_symbol"]
        response = get_lunarcrush_coins_infulencers(coin_symbol)

        return StandardResponse(
            data={"feeds": response.json()['data']}, errors=None, status_code=status.HTTP_200_OK
        )


class StreamLunarcrushFeedTweets(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsWhitelisted]

    def post(self, request, *args, **kwargs):
        serializer = GetFeedsSerializer(
            data=request.data, context={"request": request}
        )
        if not serializer.is_valid():
            return StandardResponse(
                data=None,
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        coin_symbol = serializer.validated_data["coin_symbol"]
        self.project = Project.objects.get(
            id=serializer.validated_data["project_id"], user=request.user
        )
        response = get_lunarcrush_coins_feeds(coin_symbol)
        all_tweets = response.json()['data']
        responses = []
        for tweet in all_tweets:
            content = tweet['title']
            res = get_openai_response(content)
            if "reply_text" in res and res["reply_text"].strip():
                created_tweet = Tweets.objects.create(
                    user=self.request.user,
                    project=self.project,
                    tweet_content=tweet['title'],
                    ai_response=res["reply_text"],
                    tweet_id=tweet['identifier'],
                    misc_data={},
                    state="FETCHED",
                )
                responses.append(created_tweet)
        serialized_tweets = TweetSerializer(responses, many=True)
        return StandardResponse(
            data={"responses": serialized_tweets.data}, errors=None, status_code=status.HTTP_200_OK
        )

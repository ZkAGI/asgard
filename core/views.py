import ast

import openai
import requests
from bs4 import BeautifulSoup
from django.contrib.auth import get_user_model, logout
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from twitter.models import Tweets
from twitter.serializers import TweetSerializer

from .constants import OPEN_AI_APIKEY, OPEN_AI_INSTRUCTION
from .models import Project
from .serializers import KeywordRequestSerializer, UserRegistrationSerializer

User = get_user_model()


class KeywordFetchView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = KeywordRequestSerializer(data=request.data)
        if serializer.is_valid():
            url = serializer.validated_data["url"]
            project_id = serializer.validated_data["project_id"]
            keywords, soup_text = self.fetch_keywords(url)
            self.project = Project.objects.get(id=project_id)
            self.project.keywords = keywords
            self.project.soup_text = soup_text
            self.project.save()
            return Response(
                {"data": {"keywords": keywords}},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def fetch_keywords(self, url) -> (list, str):
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        text = soup.get_text()
        while "\n\n" in text or "\t\t" in text:
            text = text.replace("\n\n", "\n").replace("\t\t", "\t")
        openai.api_key = OPEN_AI_APIKEY
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": OPEN_AI_INSTRUCTION},
                {
                    "role": "user",
                    "content": f"Domain: {url}\nlanding page text: {text.strip()}",
                },
            ],
            temperature=0.99,
            max_tokens=2431,
            top_p=1,
            frequency_penalty=0.76,
            presence_penalty=0.44,
        )
        keywords = ast.literal_eval(response.choices[0]["message"]["content"])
        return keywords, text.strip()


class UserRegistrationView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response(
                {"message": "User registered successfully", "token": token.key},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response(
            {"message": "User logged out successfully"}, status=status.HTTP_200_OK
        )


class DashboardTweets(APIView):
    def get(self, request, *args, **kwargs):
        request.user = User.objects.get(id=1)
        queryset = Tweets.objects.filter(user=request.user).order_by("-created_at")
        total_tweets = queryset.count()
        tweets_left = request.user.userprofile.tweets_left
        tweets_posted = queryset.filter(state="POSTED").count()

        paginator = PageNumberPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request)

        serializer = TweetSerializer(paginated_queryset, many=True)
        return Response(
            {
                "tweets_left": tweets_left,
                "total_tweets": total_tweets,
                "tweets_posted": tweets_posted,
                "tweets": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

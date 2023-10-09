import ast

import openai
import requests
from bs4 import BeautifulSoup
from django.contrib.auth import authenticate, get_user_model, logout
from openai.error import RateLimitError
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import APIException, NotFound
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from twitter.models import Tweets
from twitter.serializers import TweetSerializer

from .constants import OPEN_AI_APIKEY, OPEN_AI_INSTRUCTION
from .models import Project
from .serializers import (
    KeywordRequestSerializer,
    ProjectSerializer,
    UserDetailsSerializer,
    UserRegistrationSerializer,
)
from .utils import StandardResponse

User = get_user_model()


class UserDetailsView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = User.objects.get(id=request.user.id)
        serialized_user = UserDetailsSerializer(user)

        return StandardResponse(
            data=serialized_user.data,
            errors=None,
            status_code=status.HTTP_200_OK,
        )

    def put(self, request, *args, **kwargs):
        user = User.objects.get(id=request.user.id)
        serialized_user = UserDetailsSerializer(user, data=request.data)

        if serialized_user.is_valid():
            serialized_user.save()
            return StandardResponse(
                data=serialized_user.data,
                errors=None,
                status_code=status.HTTP_200_OK,
            )

        return StandardResponse(
            data=None,
            errors=serialized_user.errors,
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class UserLogoutView(APIView):
    def post(self, request):
        logout(request)
        return StandardResponse(
            data={"message": "User logged out successfully"},
            errors=None,
            status_code=status.HTTP_200_OK,
        )


class KeywordFetchView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = KeywordRequestSerializer(
            data=request.data, context={"request": request}
        )
        if not serializer.is_valid():
            return StandardResponse(
                data=None,
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        project_id = serializer.validated_data["project_id"]
        project = Project.objects.get(id=project_id)
        url = project.url
        keywords, soup_text = self.fetch_keywords(url)
        if keywords == [] or soup_text == "":
            return StandardResponse(
                data=None,
                errors={
                    "message": "Not enough content found on the requested URL, Please add keywords manually or try "
                    "again later"
                },
                status_code=status.HTTP_200_OK,
            )
        project.keywords = keywords
        project.soup_text = soup_text
        project.save()
        return StandardResponse(
            data={"keywords": keywords}, errors=None, status_code=status.HTTP_200_OK
        )

    def fetch_keywords(self, url) -> (list, str):
        response = requests.get(url, verify=False)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        text = soup.get_text()
        while "\n\n" in text or "\t\t" in text:
            text = text.replace("\n\n", "\n").replace("\t\t", "\t")
        openai.api_key = OPEN_AI_APIKEY
        if text.strip() == "":
            return [], ""
        try:
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
        except RateLimitError as e:
            return [], ""


class UserRegistrationView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if not serializer.is_valid():
            return StandardResponse(
                data=None,
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return StandardResponse(
            data={"token": token.key},
            errors=None,
            status_code=status.HTTP_201_CREATED,
        )


class UserLoginView(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")
        if username is None or password is None:
            return StandardResponse(
                data=None,
                errors={"message": "Please provide both username and password"},
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        user = authenticate(username=username, password=password)
        if not user:
            return StandardResponse(
                data=None,
                errors={"message": "Invalid credentials"},
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        token, _ = Token.objects.get_or_create(user=user)
        return StandardResponse(
            data={"token": token.key},
            errors=None,
            status_code=status.HTTP_200_OK,
        )


class DashboardTweets(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        queryset = Tweets.objects.filter(user=request.user).order_by("-created_at")
        total_tweets = queryset.count()
        tweets_left = request.user.userprofile.tweets_left
        tweets_posted = queryset.filter(state="POSTED").count()

        paginator = PageNumberPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request)

        serializer = TweetSerializer(paginated_queryset, many=True)
        return StandardResponse(
            data={
                "tweets_left": tweets_left,
                "total_tweets": total_tweets,
                "tweets_posted": tweets_posted,
                "tweets": serializer.data,
            },
            errors=None,
            status_code=status.HTTP_200_OK,
        )


class ProjectView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        projects = Project.objects.filter(user=request.user).order_by("id")
        paginator = PageNumberPagination()
        paginated_projects = paginator.paginate_queryset(projects, request)
        serializer = ProjectSerializer(paginated_projects, many=True)

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

    def post(self, request, format=None):
        serializer = ProjectSerializer(data=request.data)
        if not serializer.is_valid():
            return StandardResponse(
                data=None,
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        serializer.save(user=request.user)
        return StandardResponse(
            data=serializer.data,
            errors=None,
            status_code=status.HTTP_201_CREATED,
        )


class ProjectDetailView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Project.objects.get(pk=pk)
        except Project.DoesNotExist:
            raise NotFound(detail="Project not found")

    def get(self, request, pk, format=None):
        project = self.get_object(pk)
        serializer = ProjectSerializer(project)
        return StandardResponse(
            data=serializer.data,
            errors=None,
            status_code=status.HTTP_200_OK,
        )

    def put(self, request, pk, format=None):
        project = self.get_object(pk)
        serializer = ProjectSerializer(project, data=request.data)
        if not serializer.is_valid():
            return StandardResponse(
                data=None,
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        try:
            serializer.save()
        except Exception as e:
            raise APIException(detail=str(e))

        return StandardResponse(
            data=serializer.data,
            errors=None,
            status_code=status.HTTP_201_CREATED,
        )

    def delete(self, request, pk, format=None):
        project = self.get_object(pk)
        project.delete()
        return StandardResponse(
            data=None,
            errors=None,
            status_code=status.HTTP_204_NO_CONTENT,
        )

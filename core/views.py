import openai
import requests
from bs4 import BeautifulSoup
from django.contrib.auth import get_user_model, logout
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

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
            keywords = self.fetch_keywords(url)
            return Response({"data": keywords}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def fetch_keywords(self, url):
        response = requests.get(url)
        if response.status_code != 200:
            return Response({"error": "Given URL is not reachable"}, status=400)
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
        keywords = response.choices[0]["message"]["content"]
        return {"keywords": keywords, "soup_text": text.strip()}

    def get_project(self, project_id):
        self.project = Project.objects.get(id=project_id)


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

import re

from django.contrib.auth import get_user_model
from rest_framework import serializers

from core.constants import EMAIL_REGEX

User = get_user_model()


class UserRegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    username = serializers.CharField(max_length=30)
    password = serializers.CharField(write_only=True)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already in use")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already in use")
        if not re.match(EMAIL_REGEX, value):
            raise serializers.ValidationError("Invalid email format")

        return value

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

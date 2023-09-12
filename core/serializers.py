import re

from django.contrib.auth import get_user_model
from rest_framework import serializers

from core.constants import EMAIL_REGEX
from core.models import Project

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


class ProjectSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    url = serializers.URLField()
    name = serializers.CharField(max_length=100)
    ai_rules = serializers.CharField(allow_blank=True, required=False)
    keywords = serializers.JSONField(required=False)
    soup_text = serializers.CharField(allow_blank=True, required=False)

    def create(self, validated_data):
        return Project.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.url = validated_data.get("url", instance.url)
        instance.name = validated_data.get("name", instance.name)
        instance.ai_rules = validated_data.get("ai_rules", instance.ai_rules)
        instance.keywords = validated_data.get("keywords", instance.keywords)
        instance.soup_text = validated_data.get("soup_text", instance.soup_text)
        instance.save()
        return instance


class KeywordRequestSerializer(serializers.Serializer):
    project_id = serializers.IntegerField()

    def validate_project_id(self, value):
        request = self.context.get("request")
        try:
            project = Project.objects.get(pk=value, user=request.user)
        except Project.DoesNotExist:
            raise serializers.ValidationError(
                "Invalid project ID or you do not have permission to access this project"
            )
        return value

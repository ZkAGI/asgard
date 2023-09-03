from rest_framework import serializers

from core.models import Project
from twitter.models import Tweets


class FetchTweetRequestSerializer(serializers.Serializer):
    project_id = serializers.IntegerField()

    def validate_project_id(self, value):
        try:
            Project.objects.get(pk=value)
        except Project.DoesNotExist:
            raise serializers.ValidationError("Invalid project ID")

        return value


class TweetSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.username")
    project = serializers.ReadOnlyField(source="project.id")

    class Meta:
        model = Tweets
        fields = [
            "id",
            "user",
            "project",
            "tweet_content",
            "ai_response",
            "misc_data",
            "state",
        ]

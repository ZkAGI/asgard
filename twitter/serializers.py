from rest_framework import serializers

from core.models import Project
from twitter.models import Tweets


class FetchTweetRequestSerializer(serializers.Serializer):
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
            "created_at",
            "author_id",
            "tweet_id",
        ]


class PostTweetRequestSerializer(serializers.Serializer):
    tweet_id = serializers.IntegerField()

    def validate_tweet_id(self, value):
        request = self.context.get("request")
        try:
            tweet = Tweets.objects.get(pk=value)
        except Tweets.DoesNotExist:
            raise serializers.ValidationError("Invalid tweet ID")

        if tweet.state != "APPROVED":
            raise serializers.ValidationError("Tweet is not in APPROVED state")

        if tweet.user != request.user:
            raise serializers.ValidationError("Tweet does not belong to you")

        if tweet.state == "POSTED":
            raise serializers.ValidationError("Tweet has already been posted")

        return value

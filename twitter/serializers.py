from rest_framework import serializers

from core.models import Project, UserProfile
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

    def validate(self, data):
        user = self.context.get("request").user
        user_profile = UserProfile.objects.get(user=user)
        if user_profile.tweets_left <= 0 or user.is_active is False:
            raise serializers.ValidationError(
                "You have no tweets left or your account is not active"
            )
        return data

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

        if tweet.user != request.user:
            raise serializers.ValidationError("Tweet does not belong to you")

        return value

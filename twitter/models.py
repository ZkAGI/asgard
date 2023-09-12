from django.contrib.auth import get_user_model
from django.db import models

from core.models import BaseModel, Project

User = get_user_model()


class Tweets(BaseModel):
    TWEET_STATES = (
        ("FETCHED", "FETCHED"),
        ("APPROVED", "APPROVED"),
        ("POSTED", "POSTED"),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    tweet_content = models.TextField()
    ai_response = models.TextField(null=True, default=None)
    misc_data = models.JSONField()
    author_id = models.CharField(max_length=255)
    tweet_id = models.CharField(max_length=255)
    state = models.CharField(max_length=255, choices=TWEET_STATES)

    def __str__(self):
        return f"{self.user.username}'s Tweet - ({self.state})"


class TwitterAccount(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=255)
    access_token = models.CharField(max_length=255)
    oauth_token = models.CharField(max_length=255, null=False, blank=False)
    oauth_token_secret = models.CharField(max_length=255)
    twitter_id = models.CharField(max_length=255)

    def __str__(self):
        return self.username

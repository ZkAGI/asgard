from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True


class Project(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, null=True)
    website = models.URLField(max_length=200)
    ai_rules = models.TextField()
    keywords = models.TextField()

    def __str__(self):
        return self.name


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
    state = models.CharField(max_length=255, choices=TWEET_STATES)

    def __str__(self):
        return f"{self.user.username}'s Tweet - ({self.state})"

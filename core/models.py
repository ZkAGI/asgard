from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tweets_left = models.IntegerField(default=5000)


class Project(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    url = models.URLField()
    name = models.CharField(max_length=100)
    website = models.URLField(max_length=200)
    ai_rules = models.TextField(null=True, blank=True)
    keywords = models.TextField(null=True, blank=True)
    soup_text = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

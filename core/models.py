import json

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_whitelisted = models.BooleanField(default=False)
    tweets_left = models.PositiveIntegerField(default=2000)

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()


class Project(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    url = models.URLField()
    name = models.CharField(max_length=100)
    ai_rules = models.TextField(null=True, blank=True)
    keywords = models.JSONField(blank=True, null=True)
    soup_text = models.TextField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.keywords:
            self.keywords = json.dumps(self.keywords)
        super(Project, self).save(*args, **kwargs)

from django.contrib.auth import get_user_model
from django.db import models
from core.models import BaseModel

User = get_user_model()


class Quest(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=250)


class TGUser(BaseModel):
    userid = models.CharField(max_length=100)
    score = models.PositiveIntegerField(default=0)
    quest = models.ForeignKey(Quest, on_delete=models.CASCADE)


class TGVerifiedUsers(BaseModel):
    userid = models.CharField(max_length=100)
    otp = models.PositiveIntegerField(default=0)

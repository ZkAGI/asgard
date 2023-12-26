from django.db import models
from core.models import BaseModel


class TGUser(BaseModel):
    userid = models.CharField(max_length=100)
    score = models.PositiveIntegerField(default=0)


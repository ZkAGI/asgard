from rest_framework import serializers
from .models import TGUser

class TGUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TGUser
        fields = ['userid', 'score']

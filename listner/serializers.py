from rest_framework import serializers
from .models import TGUser, Quest


class TGUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TGUser
        fields = ['userid', 'score']


class QuestSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(max_length=100)
    description = serializers.CharField(max_length=250)

    def create(self, validated_data):
        """
        Create and return a new `Quest` instance, given the validated data.
        """
        return Quest.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Quest` instance, given the validated data.
        """
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.save()
        return instance

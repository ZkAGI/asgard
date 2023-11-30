from rest_framework import serializers


class GetFeedsSerializer(serializers.Serializer):
    coin_symbol = serializers.CharField()
    project_id = serializers.IntegerField()


class GetInfluencersSerializer(serializers.Serializer):
    coin_symbol = serializers.CharField()
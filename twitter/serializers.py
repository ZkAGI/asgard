from rest_framework import serializers

from core.models import Project


class FetchTweetRequestSerializer(serializers.Serializer):
    project_id = serializers.IntegerField()

    def validate_project_id(self, value):
        try:
            Project.objects.get(pk=value)
        except Project.DoesNotExist:
            raise serializers.ValidationError("Invalid project ID")

        return value

    def validate(self, data):
        project_id = data.get("project_id")
        project = Project.objects.get(pk=project_id)

        if project.keywords is None:
            raise serializers.ValidationError("No keywords found for this project")

        return data

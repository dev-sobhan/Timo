from rest_framework import serializers
from tasks.models import Task


class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer for Task model.

    Handles validation and serialization of task data.
    Team and creator are injected automatically from the view layer.
    """

    class Meta:
        model = Task
        fields = (
            "id",
            "title",
            "description",
            "team",
            "is_team_task",
            "file",
            "created_by",
            "status",
            "due_date",
            "created_at",
        )
        read_only_fields = (
            "id",
            "team",
            "created_by",
            "created_at",
        )

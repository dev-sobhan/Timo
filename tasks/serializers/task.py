from rest_framework import serializers
from tasks.models import Task


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ("id", "title", "description", "team", "is_team_task", "file", "created_by", "status", "due_date",
                  "created_at")
        read_only_fields = ("id", "created_at", "created_by")

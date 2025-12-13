from rest_framework import serializers
from tasks.models import TaskAssignment


class TaskAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskAssignment
        fields = ("id", "task", "member", "status", "progress", "answer", "file", "started_at", "completed_at",)
        read_only_fields = ("id", "started_at", "completed_at")

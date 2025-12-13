from rest_framework import serializers
from tasks.models import TaskNote


class TaskNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskNote
        fields = ("id", "task", "assignment", "author", "content", "is_read", "created_at",)
        read_only_fields = ("id", "is_read", "created_at")

from rest_framework import serializers
from teams.models import TeamRequest


class TeamRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamRequest
        fields = ("id", "team", "user", "status", "message", "file", "note", "created_at")
        read_only_fields = ("id", "team", "user", "status", "created_at")

from rest_framework import serializers
from teams.models import TeamMember


class TeamMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamMember
        fields = ("id", "team", "user", "role", "is_active")
        read_only_fields = ("id", "team", "user", "is_active")

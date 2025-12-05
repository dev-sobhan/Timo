from rest_framework import serializers
from teams.models import TeamRequest


class TeamRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamRequest
        fields = ("id", "team", "user", "status", "message", "file", "note", "created_at")
        read_only_fields = ("id", "user", "status", "created_at")

    def validate(self, attrs):
        user = self.context['request'].user
        team = attrs.get('team')
        if TeamRequest.objects.filter(user=user, team=team).exists():
            raise serializers.ValidationError("You have already requested membership for this team.")
        return attrs

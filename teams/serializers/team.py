from rest_framework import serializers
from teams.models import Team


class TeamSerializer(serializers.ModelSerializer):
    members_count = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = [
            'id',
            'title',
            'description',
            'is_visible',
            'is_active',
            'image',
            'status',
            'members_count',
            'created_at',
            'updated_at',
        ]

    def get_members_count(self, obj):
        return obj.members.count()

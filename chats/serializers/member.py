from rest_framework import serializers
from ..models.chat_member import ChatMember


class ChatMemberSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user.id", read_only=True)

    class Meta:
        model = ChatMember
        fields = (
            "user_id",
            "role",
            "is_muted",
            "joined_at",
        )
        read_only_fields = fields

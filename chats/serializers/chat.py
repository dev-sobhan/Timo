from rest_framework import serializers
from ..models.chat import Chat


class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = (
            "id",
            "type",
            "created_by",
            "created_at",
        )
        read_only_fields = fields


class ChatListSerializer(serializers.ModelSerializer):
    last_message_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Chat
        fields = (
            "id",
            "type",
            "last_message_at",
        )

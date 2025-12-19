from rest_framework import serializers
from ..models.private_chat import PrivateChat
from .member import ChatMemberSerializer


class PrivateChatReadSerializer(serializers.ModelSerializer):
    chat_id = serializers.IntegerField(source="chat.id", read_only=True)
    members = ChatMemberSerializer(
        source="chat.members",
        many=True,
        read_only=True,
    )

    class Meta:
        model = PrivateChat
        fields = (
            "chat_id",
            "user1",
            "user2",
            "members",
        )
        read_only_fields = fields


class PrivateChatCreateSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()

    def validate_user_id(self, value):
        request = self.context["request"]
        if value == request.user.id:
            raise serializers.ValidationError(
                "You cannot create a private chat with yourself."
            )
        return value

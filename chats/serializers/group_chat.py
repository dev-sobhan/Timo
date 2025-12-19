from rest_framework import serializers
from ..models.group_chat import GroupChat
from .member import ChatMemberSerializer


class GroupChatReadSerializer(serializers.ModelSerializer):
    chat_id = serializers.IntegerField(source="chat.id", read_only=True)
    members = ChatMemberSerializer(
        source="chat.members",
        many=True,
        read_only=True,
    )

    class Meta:
        model = GroupChat
        fields = (
            "chat_id",
            "title",
            "description",
            "avatar",
            "members",
        )
        read_only_fields = fields


class GroupChatCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True)
    avatar = serializers.ImageField(required=False)

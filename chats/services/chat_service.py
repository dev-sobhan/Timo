from django.contrib.auth import get_user_model
from django.db import transaction
from ..models.chat import Chat
from ..models.private_chat import PrivateChat
from ..models.group_chat import GroupChat
from ..models.chat_member import ChatMember

User = get_user_model()


class ChatService:
    """
    Service layer for chat-related business logic.
    This class MUST NOT depend on DRF or HTTP concepts.
    """

    @staticmethod
    @transaction.atomic
    def create_private_chat(*, user, target_user_id: int) -> PrivateChat:
        """
        Create or return an existing private chat between two users.
        This operation is idempotent and race-condition safe.
        """

        if user.id == target_user_id:
            raise ValueError("Cannot create private chat with yourself.")

        try:
            target_user = User.objects.only("id").get(id=target_user_id)
        except User.DoesNotExist:
            raise ValueError("Target user does not exist.")

        # enforce ordering to prevent duplicate pairs
        user1, user2 = (
            (user, target_user)
            if user.id < target_user.id
            else (target_user, user)
        )

        # Try to get existing private chat
        private_chat = (
            PrivateChat.objects
            .select_related("chat")
            .filter(user1=user1, user2=user2)
            .first()
        )

        if private_chat:
            return private_chat

        # Create chat
        chat = Chat.objects.create(
            type=Chat.PRIVATE,
            created_by=user,
        )

        private_chat = PrivateChat.objects.create(
            chat=chat,
            user1=user1,
            user2=user2,
        )

        # Add members
        ChatMember.objects.bulk_create([
            ChatMember(
                chat=chat,
                user=user1,
                role=ChatMember.MEMBER,
            ),
            ChatMember(
                chat=chat,
                user=user2,
                role=ChatMember.MEMBER,
            ),
        ])

        return private_chat

    @staticmethod
    @transaction.atomic
    def create_group_chat(*, user, data: dict) -> GroupChat:
        """
        Create a new group chat and assign creator as owner.
        """

        chat = Chat.objects.create(
            type=Chat.GROUP,
            created_by=user,
        )

        group_chat = GroupChat.objects.create(
            chat=chat,
            title=data["title"],
            description=data.get("description", ""),
            avatar=data.get("avatar"),
        )

        ChatMember.objects.create(
            chat=chat,
            user=user,
            role=ChatMember.OWNER,
        )

        return group_chat

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


class PresenceService:
    PREFIX = "chat_presence"

    @classmethod
    def group_name(cls, chat_id: int) -> str:
        return f"{cls.PREFIX}_{chat_id}"

    @classmethod
    def user_key(cls, chat_id: int, user_id: int) -> str:
        return f"{cls.PREFIX}:{chat_id}:{user_id}"

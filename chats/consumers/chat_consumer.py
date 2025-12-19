import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from ..models.chat_member import ChatMember
from ..mongo.message_repository import MessageRepository


class ChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for chat (private & group).

    Features:
      - JWT auth via middleware (scope["user"])
      - Mongo message persistence
      - Broadcast events: message, typing, seen, presence
      - Async & high-performance
    """

    async def connect(self):
        self.user = self.scope["user"]
        self.chat_id = int(self.scope["url_route"]["kwargs"]["chat_id"])
        self.group_name = f"chat_{self.chat_id}"

        # 1️⃣ Authentication
        if not self.user or not self.user.is_authenticated:
            await self.close(code=4001)
            return

        # 2️⃣ Authorization: check membership
        is_member = await self._is_chat_member()
        if not is_member:
            await self.close(code=4003)
            return

        # 3️⃣ Join channel group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

        # 4️⃣ Notify presence
        await self._broadcast_event(
            event="user_online",
            payload={"user_id": self.user.id},
        )

    async def disconnect(self, close_code):
        # Leave group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

        # Broadcast offline
        await self._broadcast_event(
            event="user_offline",
            payload={"user_id": self.user.id},
        )

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        event = data.get("event")

        # Event dispatch
        handlers = {
            "typing": self._handle_typing,
            "seen": lambda: self._handle_seen(data),
            "message": lambda: self._handle_message(data),
        }

        handler = handlers.get(event)
        if handler:
            await handler()

    async def _handle_typing(self):
        await self._broadcast_event(
            event="typing",
            payload={"user_id": self.user.id},
        )

    async def _handle_seen(self, data):
        await self._broadcast_event(
            event="seen",
            payload={
                "user_id": self.user.id,
                "message_id": data.get("message_id"),
            },
        )

    async def _handle_message(self, data):
        """
        Persist message to MongoDB and broadcast to group.
        """
        content = data.get("content")
        msg_type = data.get("type", "text")
        reply_to = data.get("reply_to")
        file_data = data.get("file")  # optional, dict with file info

        # 1️⃣ Save to Mongo
        message = await database_sync_to_async(MessageRepository.create_message)(
            chat_id=self.chat_id,
            sender_id=self.user.id,
            content=content,
            message_type=msg_type,
            file=file_data,
            reply_to=reply_to,
        )

        # 2️⃣ Broadcast
        await self._broadcast_event(
            event="message",
            payload={
                "id": str(message["_id"]),
                "user_id": self.user.id,
                "content": content,
                "type": msg_type,
                "file": file_data,
                "reply_to": reply_to,
                "created_at": message["created_at"].isoformat(),
            },
        )

    async def chat_event(self, event):
        await self.send(text_data=json.dumps(event["data"]))

    async def _broadcast_event(self, *, event: str, payload: dict):
        """
        Broadcast a generic chat event to the group.
        """
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "chat.event",
                "data": {
                    "event": event,
                    **payload,
                },
            },
        )

    @database_sync_to_async
    def _is_chat_member(self) -> bool:
        """
        Check if the user is member of the chat (private/group)
        """
        return ChatMember.objects.filter(
            chat_id=self.chat_id,
            user=self.user,
        ).exists()

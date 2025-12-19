from typing import List, Optional
from datetime import datetime

from bson import ObjectId

from .client import MongoConnection


class MessageRepository:
    """
    MongoDB repository for chat messages.
    """

    COLLECTION_NAME = "messages"

    @classmethod
    def _collection(cls):
        return MongoConnection.get_db()[cls.COLLECTION_NAME]

    @classmethod
    def create_message(
            cls,
            *,
            chat_id: int,
            sender_id: int,
            content: str,
            message_type: str = "text",
            file: Optional[dict] = None,
            reply_to: Optional[str] = None,
    ) -> dict:
        document = {
            "chat_id": chat_id,
            "sender_id": sender_id,
            "type": message_type,
            "content": content,
            "file": file,
            "reply_to": ObjectId(reply_to) if reply_to else None,
            "created_at": datetime.utcnow(),
            "edited_at": None,
            "deleted": False,
        }

        result = cls._collection().insert_one(document)
        document["_id"] = result.inserted_id
        return document

    @classmethod
    def fetch_messages(
            cls,
            *,
            chat_id: int,
            limit: int = 100,
            before: Optional[str] = None,
    ) -> List[dict]:
        query = {
            "chat_id": chat_id,
            "deleted": False,
        }

        if before:
            query["_id"] = {"$lt": ObjectId(before)}

        cursor = (
            cls._collection()
            .find(query)
            .sort("_id", -1)
            .limit(limit)
        )

        messages = list(cursor)
        messages.reverse()  # oldest → newest
        return messages

    @classmethod
    def soft_delete_message(cls, *, message_id: str, user_id: int) -> bool:
        result = cls._collection().update_one(
            {
                "_id": ObjectId(message_id),
                "sender_id": user_id,
            },
            {
                "$set": {
                    "deleted": True,
                    "edited_at": datetime.utcnow(),
                }
            },
        )
        return result.modified_count == 1

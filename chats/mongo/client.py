from pymongo import MongoClient
from django.conf import settings


class MongoConnection:
    _client = None

    @classmethod
    def get_client(cls) -> MongoClient:
        if cls._client is None:
            cls._client = MongoClient(settings.MONGO_URI)
        return cls._client

    @classmethod
    def get_db(cls):
        return cls.get_client()[settings.MONGO_DB_NAME]

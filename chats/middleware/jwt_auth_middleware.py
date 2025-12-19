import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from urllib.parse import parse_qs

User = get_user_model()


@database_sync_to_async
def get_user(user_id):
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return None


class JWTAuthMiddleware(BaseMiddleware):
    """
    JWT Authentication for WebSocket connections.
    Reads token from query string: ws://.../?token=<jwt>
    """

    async def __call__(self, scope, receive, send):
        # Parse token from query string
        query_string = scope.get("query_string", b"").decode()
        qs = parse_qs(query_string)
        token_list = qs.get("token", [])

        if not token_list:
            scope["user"] = None
            return await super().__call__(scope, receive, send)

        token = token_list[0]

        try:
            payload = jwt.decode(
                token,
                settings.SIMPLE_JWT["SIGNING_KEY"],
                algorithms=[settings.SIMPLE_JWT["ALGORITHM"]],
            )
            user = await get_user(payload["user_id"])
            scope["user"] = user
        except Exception:
            scope["user"] = None

        return await super().__call__(scope, receive, send)

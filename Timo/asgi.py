from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import chats.routing
from chats.middleware.jwt_auth_middleware import JWTAuthMiddleware

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": JWTAuthMiddleware(
        URLRouter(
            chats.routing.websocket_urlpatterns
        )
    ),
})

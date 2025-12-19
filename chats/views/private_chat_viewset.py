from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiResponse

from utils.response import success_response, error_response
from chats.errors.loader import get_error
from ..serializers.private_chat import (
    PrivateChatCreateSerializer,
    PrivateChatReadSerializer,
)
from ..services.chat_service import ChatService


class PrivateChatViewSet(ModelViewSet):
    """
    Create private chats between two users.
    """

    permission_classes = (IsAuthenticated,)
    http_method_names = ["post"]

    def get_serializer_class(self):
        if self.action == "create":
            return PrivateChatCreateSerializer
        return PrivateChatReadSerializer

    @extend_schema(
        summary="Create or get private chat",
        description=(
                "Creates a private chat with another user. "
                "If a private chat already exists, it will be returned instead."
        ),
        request=PrivateChatCreateSerializer,
        responses={
            201: OpenApiResponse(
                description="Private chat created or returned",
                response=PrivateChatReadSerializer
            ),
            400: OpenApiResponse(description="Invalid request")
        }
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return error_response(
                error_dict=get_error(key="CHATS_001002", details=serializer.errors),
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            private_chat = ChatService.create_private_chat(
                user=request.user,
                target_user_id=serializer.validated_data["user_id"],
            )
        except Exception as exc:
            return error_response(
                error_dict=get_error(key="CHAT_001002", details=str(exc)),
                status=status.HTTP_400_BAD_REQUEST
            )

        read_serializer = PrivateChatReadSerializer(private_chat)
        return success_response(read_serializer.data, status=status.HTTP_201_CREATED)

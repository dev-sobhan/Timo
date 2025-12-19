from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiResponse
from utils.response import success_response, error_response
from chats.errors.loader import get_error
from ..models.group_chat import GroupChat
from ..serializers.group_chat import (
    GroupChatCreateSerializer,
    GroupChatReadSerializer,
)
from ..services.chat_service import ChatService


class GroupChatViewSet(ModelViewSet):
    """
    Manage group chats.
    """

    permission_classes = (IsAuthenticated,)
    queryset = GroupChat.objects.select_related("chat")
    http_method_names = ["post", "get"]

    def get_serializer_class(self):
        if self.action == "create":
            return GroupChatCreateSerializer
        return GroupChatReadSerializer

    def get_queryset(self):
        return self.queryset.filter(chat__members__user=self.request.user)

    @extend_schema(
        summary="Create group chat",
        description="Creates a new group chat and assigns the creator as owner.",
        request=GroupChatCreateSerializer,
        responses={
            201: OpenApiResponse(
                description="Group chat created",
                response=GroupChatReadSerializer
            )
        }
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return error_response(
                error_dict=get_error(key="CHATS_001001", details=serializer.errors),
                status=status.HTTP_400_BAD_REQUEST
            )

        group_chat = ChatService.create_group_chat(
            user=request.user,
            data=serializer.validated_data,
        )

        read_serializer = GroupChatReadSerializer(group_chat)
        return success_response(read_serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="List user group chats",
        description="Returns all group chats the authenticated user is a member of.",
        responses={
            200: OpenApiResponse(
                description="List of group chats",
                response=GroupChatReadSerializer
            )
        }
    )
    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return success_response(serializer.data)

from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiResponse

from utils.response import success_response
from ..models.chat import Chat
from ..serializers.chat import ChatListSerializer, ChatSerializer


class ChatViewSet(ReadOnlyModelViewSet):
    """
    List and retrieve chats that the authenticated user is a member of.
    """

    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return (
            Chat.objects
            .filter(members__user=self.request.user)
            .distinct()
            .select_related("created_by")
        )

    def get_serializer_class(self):
        if self.action == "list":
            return ChatListSerializer
        return ChatSerializer

    @extend_schema(
        summary="List user chats",
        description="Returns all chats (private and group) the authenticated user is a member of.",
        responses={
            200: OpenApiResponse(
                description="List of user chats",
                response=ChatListSerializer
            )
        }
    )
    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return success_response(serializer.data)

    @extend_schema(
        summary="Retrieve chat details",
        description="Returns base information about a specific chat.",
        responses={
            200: OpenApiResponse(
                description="Chat details",
                response=ChatSerializer
            )
        }
    )
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(serializer.data)

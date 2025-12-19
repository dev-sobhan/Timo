from django.urls import path
from .views import (PrivateChatViewSet, ChatViewSet, GroupChatViewSet, ChatMessageListApi)

app_name = "chats"

urlpatterns = [

    # Private chat
    path(
        "private/",
        PrivateChatViewSet.as_view({"post": "create"}),
        name="chat_private_create"
    ),

    # Group chats
    path(
        "groups/",
        GroupChatViewSet.as_view({"get": "list", "post": "create"}),
        name="chat_group"
    ),
    path(
        "groups/<int:pk>/",
        GroupChatViewSet.as_view({"get": "retrieve"}),
        name="chat_group_detail"
    ),

    path("messages/<chat_id>/", ChatMessageListApi.as_view(), name="get_messages"),

    # Chats
    path(
        "",
        ChatViewSet.as_view({"get": "list"}),
        name="chat_list"
    ),
    path(
        "<int:pk>/",
        ChatViewSet.as_view({"get": "retrieve"}),
        name="chat_detail"
    ),
]

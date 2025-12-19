from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from users.tests.factories import UserFactory
from chats.models import Chat, ChatMember, GroupChat
from chats.services.chat_service import ChatService


class GroupChatViewSetTestCase(APITestCase):

    def setUp(self):
        self.user = UserFactory()
        self.user2 = UserFactory()
        self.client.force_authenticate(user=self.user)

        # Create a group chat for list test
        chat = Chat.objects.create(type=Chat.GROUP, created_by=self.user)
        self.group_chat = GroupChat.objects.create(
            chat=chat,
            title="Test Group",
            description="Sample description"
        )
        ChatMember.objects.create(chat=chat, user=self.user, role=ChatMember.OWNER)

        # URLs
        self.list_url = reverse("chats:chat_group")
        self.create_url = self.list_url  # create uses same endpoint in DRF ModelViewSet

    def test_list_group_chats_authenticated_user(self):
        """List only group chats that the authenticated user is a member of"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data["data"]
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["title"], "Test Group")

    def test_create_group_chat_success(self):
        """Create a new group chat successfully"""
        data = {
            "title": "New Group",
            "description": "Created via test",
        }
        response = self.client.post(self.create_url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(GroupChat.objects.filter(title="New Group").exists())

        # Verify owner is assigned
        group_chat = GroupChat.objects.get(title="New Group")
        member = ChatMember.objects.get(chat=group_chat.chat, user=self.user)
        self.assertEqual(member.role, ChatMember.OWNER)

    def test_create_group_chat_fail_invalid_data(self):
        """Attempt to create group chat with invalid data"""
        data = {"title": ""}  # title is required
        response = self.client.post(self.create_url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])

    def test_list_requires_authentication(self):
        """Unauthenticated users cannot list group chats"""
        self.client.force_authenticate(user=None)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_requires_authentication(self):
        """Unauthenticated users cannot create group chat"""
        self.client.force_authenticate(user=None)
        data = {"title": "Unauthorized Group"}
        response = self.client.post(self.create_url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

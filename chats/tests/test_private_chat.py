from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch
from users.tests.factories import UserFactory
from chats.models import Chat, ChatMember, PrivateChat
from chats.services.chat_service import ChatService


class PrivateChatViewSetTestCase(APITestCase):

    def setUp(self):
        self.user = UserFactory()
        self.user2 = UserFactory()
        self.client.force_authenticate(user=self.user)

        self.create_url = reverse("chats:chat_private_create")

    @patch("chats.errors.loader.get_error", return_value={"code": "CHATS_001002", "message": "Invalid data"})
    def test_create_private_chat_success(self, mock_get_error):
        """Create a new private chat successfully"""
        data = {"user_id": self.user2.id}
        response = self.client.post(self.create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        private_chat = PrivateChat.objects.get(user1__in=[self.user, self.user2], user2__in=[self.user, self.user2])
        self.assertIsNotNone(private_chat)
        self.assertIn(self.user, [private_chat.user1, private_chat.user2])
        self.assertIn(self.user2, [private_chat.user1, private_chat.user2])

        members = ChatMember.objects.filter(chat=private_chat.chat)
        self.assertEqual(members.count(), 2)
        self.assertTrue(members.filter(user=self.user).exists())
        self.assertTrue(members.filter(user=self.user2).exists())

    @patch("chats.errors.loader.get_error", return_value={"code": "CHATS_001002", "message": "Invalid data"})
    def test_create_private_chat_fail_invalid_data(self, mock_get_error):
        """Attempt to create private chat with invalid data"""
        data = {"user_id": ""}
        response = self.client.post(self.create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])

    @patch("chats.errors.loader.get_error", return_value={"code": "CHAT_001002", "message": "Cannot chat with yourself"})
    def test_create_private_chat_with_self(self, mock_get_error):
        """Cannot create private chat with yourself"""
        data = {"user_id": self.user.id}
        response = self.client.post(self.create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])

    def test_create_private_chat_requires_authentication(self):
        """Unauthenticated users cannot create private chat"""
        self.client.force_authenticate(user=None)
        data = {"user_id": self.user2.id}
        response = self.client.post(self.create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

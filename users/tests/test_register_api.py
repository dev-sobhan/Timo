from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from users.models import User
from users.tests.factories import UserFactory
from rest_framework_simplejwt.tokens import RefreshToken


class RegisterAPITestCase(APITestCase):
    def setUp(self):
        self.url = reverse("users:register")
        self.valid_data = {
            "full_name": "Test User",
            "email": "testuser@example.com",
            "password": "StrongPass123"
        }

    def authenticate_user(self, client, user):
        """
        Helper function to authenticate a user in tests with JWT.
        """
        refresh = RefreshToken.for_user(user)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def test_register_success(self):
        response = self.client.post(self.url, self.valid_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertIsNone(response.data["error"])
        self.assertTrue(User.objects.filter(email=self.valid_data["email"]).exists())

    def test_register_fail_missing_email(self):
        data = self.valid_data.copy()
        data.pop("email")
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])

    def test_register_fail_existing_email(self):
        UserFactory(email=self.valid_data["email"])
        response = self.client.post(self.url, self.valid_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertIsNone(response.data["data"])

    def test_register_fail_weak_password(self):
        data = self.valid_data.copy()
        data["password"] = "123"
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertIsNone(response.data["data"])

    def test_register_fail_authenticated_user(self):
        user = UserFactory()
        self.authenticate_user(self.client, user)
        response = self.client.post(self.url, self.valid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from users.tests.factories import UserFactory
from rest_framework_simplejwt.tokens import RefreshToken


class ProfileAPITestCase(APITestCase):

    def setUp(self):
        self.url = reverse("users:profile")
        self.user = UserFactory()
        self.profile = self.user.profile
        self.authenticate(self.user)

    def authenticate(self, user):
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def test_get_profile_success(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])

        profile_data = response.data["data"]

        self.assertEqual(profile_data["user"]["id"], self.user.id)
        self.assertEqual(profile_data["user"]["full_name"], self.user.full_name)

    def test_get_profile_unauthenticated(self):
        self.client.credentials()  # remove token

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_profile_success(self):
        data = {
            "bio": "New bio updated!",
            "job_title": "Backend Developer",
            "location": "Tehran",
            "linkedin": "https://linkedin.com/test",
            "user": {
                "full_name": "New Full Name"
            }
        }

        response = self.client.patch(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])

        self.profile.refresh_from_db()
        self.user.refresh_from_db()

        self.assertEqual(self.profile.bio, "New bio updated!")
        self.assertEqual(self.profile.job_title, "Backend Developer")
        self.assertEqual(self.user.full_name, "New Full Name")

    def test_update_profile_invalid_field(self):
        data = {"birth_date": "not-a-date"}

        response = self.client.patch(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertIn("birth_date", response.data["error"]["detail"])

    def test_update_profile_unauthenticated(self):
        self.client.credentials()  # remove token
        response = self.client.patch(self.url, {"bio": "test"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_email_cannot_be_updated(self):
        old_email = self.user.email

        response = self.client.patch(
            self.url,
            {"user": {"email": "newemail@example.com"}},
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()

        self.assertEqual(self.user.email, old_email)

    def test_update_profile_birth_date_valid(self):
        data = {"birth_date": "1990-05-20"}
        response = self.client.patch(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.profile.refresh_from_db()
        self.assertEqual(
            str(self.profile.birth_date),
            "1990-05-20"
        )

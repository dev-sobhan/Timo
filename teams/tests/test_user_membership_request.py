from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from teams.models import Team, TeamMember
from users.tests.factories import UserFactory
from teams.models import TeamRequest


class MembershipRequestViewSetTestCase(APITestCase):

    def setUp(self):
        self.user = UserFactory()
        self.user2 = UserFactory()
        self.client.force_authenticate(user=self.user)

        self.team = Team.objects.create(title="Team A", description="Test team")
        TeamMember.objects.create(team=self.team, user=self.user2, role="owner")

        self.list_url = reverse("teams:membership_request")
        self.detail_url = lambda pk: reverse("teams:membership_request_detail", kwargs={"pk": pk})

    def test_create_membership_request_success(self):
        data = {"team": self.team.id, "message": "Please accept me"}

        response = self.client.post(self.list_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            TeamRequest.objects.filter(team=self.team, user=self.user).exists()
        )

    def test_create_membership_request_duplicate(self):
        TeamRequest.objects.create(team=self.team, user=self.user)

        data = {"team": self.team.id}

        response = self.client.post(self.list_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_membership_requests_only_user_own(self):
        TeamRequest.objects.create(team=self.team, user=self.user)
        TeamRequest.objects.create(team=self.team, user=self.user2)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]["user"], self.user.id)

    def test_retrieve_membership_request_success(self):
        req = TeamRequest.objects.create(team=self.team, user=self.user)

        response = self.client.get(self.detail_url(req.id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']["id"], req.id)
        self.assertEqual(response.data['data']["user"], self.user.id)

    def test_retrieve_membership_request_not_owner(self):
        req = TeamRequest.objects.create(team=self.team, user=self.user2)

        response = self.client.get(self.detail_url(req.id))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthenticated_access_blocked(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

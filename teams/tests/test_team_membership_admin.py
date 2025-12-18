from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from teams.models import Team, TeamMember, TeamRequest
from users.tests.factories import UserFactory


class TeamMembershipAdminViewSetTestCase(APITestCase):
    """
    Comprehensive tests for TeamMembershipAdminViewSet
    """

    def setUp(self):
        # Users
        self.user_owner = UserFactory()
        self.user_member = UserFactory()
        self.user_other = UserFactory()

        # Authenticate as owner/admin
        self.client.force_authenticate(user=self.user_owner)

        # Team and members
        self.team = Team.objects.create(title="Team A", description="Test team")
        TeamMember.objects.create(team=self.team, user=self.user_owner, role="owner")

        # Membership requests
        self.request_pending = TeamRequest.objects.create(team=self.team, user=self.user_member)
        self.request_other = TeamRequest.objects.create(team=self.team, user=self.user_other, status='accepted')

        # URLs
        self.list_url = reverse("teams:membership_request_list")
        self.list_team_url = reverse("teams:membership_request_admin_team", kwargs={"pk": self.team.id})
        self.detail_url = lambda pk: reverse("teams:membership_request_detail_admin",
                                             kwargs={"pk": self.request_pending.id})

    def test_list_all_pending_requests_for_user_teams(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Only pending requests should appear
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['id'], self.request_pending.id)

    def test_list_pending_requests_for_specific_team(self):
        response = self.client.get(self.list_team_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['team'], self.team.id)

    def test_retrieve_membership_request(self):
        response = self.client.get(self.detail_url(self.request_pending.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['id'], self.request_pending.id)
        self.assertEqual(response.data['data']['user'], self.user_member.id)

    def test_accept_membership_request(self):
        response = self.client.patch(self.detail_url(self.request_pending.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.request_pending.refresh_from_db()
        self.assertEqual(self.request_pending.status, 'accepted')

    def test_reject_membership_request(self):
        response = self.client.delete(self.detail_url(self.request_pending.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.request_pending.refresh_from_db()
        self.assertEqual(self.request_pending.status, 'rejected')

    def test_unauthenticated_access_blocked(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

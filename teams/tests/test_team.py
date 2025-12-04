from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from teams.models import Team, TeamMember
from users.tests.factories import UserFactory


class TeamViewSetTestCase(APITestCase):

    def setUp(self):
        self.user = UserFactory()
        self.user2 = UserFactory()
        self.client.force_authenticate(user=self.user)

        # Sample team
        self.team = Team.objects.create(title="Test Team", description="A test team")
        TeamMember.objects.create(team=self.team, user=self.user, role="owner")
        TeamMember.objects.create(team=self.team, user=self.user2, role="member")

        self.create_url = reverse("teams:team-list")
        self.my_teams_url = reverse("teams:team-my-teams")
        self.public_teams_url = reverse("teams:team-public-list")
        self.detail_url = lambda pk: reverse("teams:team-detail", kwargs={"pk": pk})
        self.activate_url = lambda pk: reverse("teams:team-activate", kwargs={"pk": pk})
        self.deactivate_url = lambda pk: reverse("teams:team-deactivate",
                                                 kwargs={"pk": pk})

    def test_create_team_success(self):
        data = {"title": "New Team", "description": "Created via test"}
        response = self.client.post(self.create_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Team.objects.filter(title="New Team").exists())
        team = Team.objects.get(title="New Team")
        owner_member = TeamMember.objects.get(team=team, user=self.user)
        self.assertEqual(owner_member.role, "owner")

    def test_create_team_fail_invalid_data(self):
        data = {"title": ""}  # Empty title
        response = self.client.post(self.create_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])

    def test_my_teams(self):
        response = self.client.get(self.my_teams_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 1)
        self.assertEqual(response.data["data"][0]["title"], self.team.title)

    def test_public_teams(self):
        self.team.is_visible = True
        self.team.is_active = True
        self.team.save()
        response = self.client.get(self.public_teams_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.team.title, [t["title"] for t in response.data["data"]])

    def test_partial_update_team_owner(self):
        data = {"description": "Updated Description"}
        response = self.client.patch(self.detail_url(self.team.pk), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.team.refresh_from_db()
        self.assertEqual(self.team.description, "Updated Description")

    def test_partial_update_team_not_owner_or_admin(self):
        self.client.force_authenticate(user=self.user2)
        data = {"description": "Hack Attempt"}
        response = self.client.patch(self.detail_url(self.team.pk), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_activate_team_owner(self):
        self.team.is_active = False
        self.team.save()
        response = self.client.patch(self.activate_url(self.team.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.team.refresh_from_db()
        self.assertTrue(self.team.is_active)

    def test_deactivate_team_owner(self):
        response = self.client.patch(self.deactivate_url(self.team.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.team.refresh_from_db()
        self.assertFalse(self.team.is_active)

    def test_unauthenticated_user_cannot_create_or_update(self):
        self.client.logout()
        response = self.client.post(self.create_url, {"title": "Test"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(self.detail_url(self.team.pk), {"description": "X"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

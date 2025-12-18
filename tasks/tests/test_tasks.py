from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from teams.models import Team, TeamMember
from tasks.models import Task
from users.tests.factories import UserFactory


class TaskViewSetTestCase(APITestCase):
    """
    Test suite for TaskViewSet.

    Covers:
    - Create task
    - List team tasks
    - Retrieve task
    - Partial update task
    - Permission checks
    """

    def setUp(self):
        # Users
        self.owner = UserFactory()
        self.member = UserFactory()
        self.outsider = UserFactory()

        self.client.force_authenticate(user=self.owner)

        # Team
        self.team = Team.objects.create(
            title="Test Team",
            description="Team for task testing"
        )

        # Team members
        TeamMember.objects.create(
            team=self.team,
            user=self.owner,
            role="owner"
        )
        TeamMember.objects.create(
            team=self.team,
            user=self.member,
            role="member"
        )

        # Sample task
        self.task = Task.objects.create(
            title="Initial Task",
            description="Initial Description",
            team=self.team,
            created_by=TeamMember.objects.get(team=self.team, user=self.owner)
        )

        # URLs
        self.team_tasks_url = lambda team_id: reverse(
            "tasks:team_tasks",
            kwargs={"team_id": team_id}
        )
        self.task_detail_url = lambda pk: reverse(
            "tasks:task",
            kwargs={"pk": pk}
        )

    def test_create_task_success_owner(self):
        data = {
            "title": "New Task",
            "description": "Created via test",
            "status": "active"
        }

        response = self.client.post(
            self.team_tasks_url(self.team.id),
            data,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Task.objects.filter(title="New Task").exists())

    def test_create_task_forbidden_for_non_admin_member(self):
        self.client.force_authenticate(user=self.member)

        data = {
            "title": "Unauthorized Task"
        }

        response = self.client.post(
            self.team_tasks_url(self.team.id),
            data,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_tasks_owner(self):
        response = self.client.get(
            self.team_tasks_url(self.team.id)
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 1)
        self.assertEqual(
            response.data["data"][0]["title"],
            self.task.title
        )

    def test_retrieve_task_owner(self):
        response = self.client.get(
            self.task_detail_url(self.task.id)
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["title"], self.task.title)

    def test_partial_update_task_owner(self):
        data = {
            "description": "Updated via test"
        }

        response = self.client.patch(
            self.task_detail_url(self.task.id),
            data,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.description, "Updated via test")

    def test_partial_update_task_forbidden_for_member(self):
        self.client.force_authenticate(user=self.member)

        data = {
            "description": "Illegal update"
        }

        response = self.client.patch(
            self.task_detail_url(self.task.id),
            data,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # --------------------------------------------------
    # Authentication
    # --------------------------------------------------

    def test_unauthenticated_user_cannot_access_tasks(self):
        self.client.logout()

        response = self.client.get(
            self.team_tasks_url(self.team.id)
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.post(
            self.team_tasks_url(self.team.id),
            {"title": "X"},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

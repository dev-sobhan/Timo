from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from users.tests.factories import UserFactory
from teams.models import Team, TeamMember
from tasks.models import Task, TaskAssignment


class TaskAssignmentViewSetTestCase(APITestCase):
    def setUp(self):
        # Users
        self.owner_user = UserFactory()
        self.admin_user = UserFactory()
        self.member_user = UserFactory()
        self.non_member_user = UserFactory()

        # Team
        self.team = Team.objects.create(title="Test Team", description="Team for testing")
        TeamMember.objects.create(team=self.team, user=self.owner_user, role="owner")
        TeamMember.objects.create(team=self.team, user=self.admin_user, role="admin")
        TeamMember.objects.create(team=self.team, user=self.member_user, role="member")

        # Task
        self.task = Task.objects.create(
            title="Test Task",
            description="Task Description",
            team=self.team,
            is_team_task=True,
            created_by=TeamMember.objects.get(team=self.team, user=self.owner_user)
        )

        # Assignment
        self.assignment_member = TaskAssignment.objects.create(
            task=self.task,
            member=TeamMember.objects.get(team=self.team, user=self.member_user),
            status="assigned",
            progress=0
        )

        # URLs
        self.list_create_url = reverse("tasks:task_assignments", kwargs={"task_id": self.task.id})
        self.detail_url = lambda pk: reverse("tasks:task_assignment_detail", kwargs={"pk": pk})

    def test_create_assignment_owner(self):
        self.client.force_authenticate(user=self.owner_user)
        member = TeamMember.objects.get(team=self.team, user=self.member_user)
        data = {"member": member.id, "status": "assigned"}

        response = self.client.post(self.list_create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TaskAssignment.objects.filter(task=self.task).count(), 2)

    def test_create_assignment_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        member = TeamMember.objects.get(team=self.team, user=self.member_user)
        data = {"member": member.id, "status": "assigned"}

        response = self.client.post(self.list_create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_assignment_member_forbidden(self):
        self.client.force_authenticate(user=self.member_user)
        member = TeamMember.objects.get(team=self.team, user=self.member_user)
        data = {"member": member.id, "status": "assigned"}

        response = self.client.post(self.list_create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_assignment_non_member(self):
        self.client.force_authenticate(user=self.non_member_user)
        data = {"member": 1, "status": "assigned"}
        response = self.client.post(self.list_create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_assignments_owner(self):
        self.client.force_authenticate(user=self.owner_user)
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 1)

    def test_list_assignments_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_assignments_member(self):
        self.client.force_authenticate(user=self.member_user)
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Member should see only their assignment
        self.assertEqual(len(response.data["data"]), 1)
        self.assertEqual(response.data["data"][0]["member"], self.assignment_member.member.id)

    def test_list_assignments_non_member_forbidden(self):
        self.client.force_authenticate(user=self.non_member_user)
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 0)  # Non-member sees nothing

    def test_retrieve_assignment_owner(self):
        self.client.force_authenticate(user=self.owner_user)
        response = self.client.get(self.detail_url(self.assignment_member.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_assignment_member(self):
        self.client.force_authenticate(user=self.member_user)
        response = self.client.get(self.detail_url(self.assignment_member.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_assignment_non_member_forbidden(self):
        self.client.force_authenticate(user=self.non_member_user)
        response = self.client.get(self.detail_url(self.assignment_member.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_partial_update_assignment_owner(self):
        self.client.force_authenticate(user=self.owner_user)
        data = {"status": "in_progress", "progress": 50}
        response = self.client.patch(self.detail_url(self.assignment_member.id), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assignment_member.refresh_from_db()
        self.assertEqual(self.assignment_member.status, "in_progress")
        self.assertEqual(self.assignment_member.progress, 50)

    def test_partial_update_assignment_member(self):
        self.client.force_authenticate(user=self.member_user)
        data = {"status": "done", "progress": 100}
        response = self.client.patch(self.detail_url(self.assignment_member.id), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assignment_member.refresh_from_db()
        self.assertEqual(self.assignment_member.status, "done")
        self.assertEqual(self.assignment_member.progress, 100)

    def test_partial_update_assignment_non_member_forbidden(self):
        self.client.force_authenticate(user=self.non_member_user)
        data = {"status": "done"}
        response = self.client.patch(self.detail_url(self.assignment_member.id), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_cannot_access(self):
        self.client.logout()
        # List
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # Create
        response = self.client.post(self.list_create_url, {"member": 1}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # Retrieve
        response = self.client.get(self.detail_url(self.assignment_member.id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # Patch
        response = self.client.patch(self.detail_url(self.assignment_member.id), {"status": "done"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from users.tests.factories import UserFactory
from teams.models import Team, TeamMember
from tasks.models import Task, TaskAssignment, TaskNote


class TaskNoteViewSetTestCase(APITestCase):
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

        # TaskNote
        self.note_by_admin = TaskNote.objects.create(
            task=self.task,
            assignment=self.assignment_member,
            author=TeamMember.objects.get(team=self.team, user=self.admin_user),
            content="Admin note",
        )
        self.note_by_member = TaskNote.objects.create(
            task=self.task,
            assignment=self.assignment_member,
            author=TeamMember.objects.get(team=self.team, user=self.member_user),
            content="Member note",
        )

        # URLs
        self.list_create_url = reverse("tasks:task_notes", kwargs={"task_id": self.task.id})
        self.detail_url = lambda pk: reverse("tasks:task_note_detail", kwargs={"pk": pk})

    def test_create_note_owner(self):
        self.client.force_authenticate(user=self.owner_user)
        data = {"content": "Owner note"}
        response = self.client.post(self.list_create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_note_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {"content": "Admin note 2"}
        response = self.client.post(self.list_create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_note_member(self):
        self.client.force_authenticate(user=self.member_user)
        data = {"content": "Member note 2"}
        response = self.client.post(self.list_create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_note_non_member_forbidden(self):
        self.client.force_authenticate(user=self.non_member_user)
        data = {"content": "Hack note"}
        response = self.client.post(self.list_create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_notes_owner(self):
        self.client.force_authenticate(user=self.owner_user)
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Owner/Admin should see member notes only
        self.assertTrue(all(n["author"] != self.owner_user.id for n in response.data["data"]))

    def test_list_notes_member(self):
        self.client.force_authenticate(user=self.member_user)
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Member should see admin notes only
        self.assertTrue(all(n["author"] != self.member_user.id for n in response.data["data"]))

    def test_list_notes_non_member(self):
        self.client.force_authenticate(user=self.non_member_user)
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Non-member sees nothing
        self.assertEqual(len(response.data["data"]), 0)

    def test_retrieve_note_marks_read_for_member(self):
        self.client.force_authenticate(user=self.member_user)
        # Retrieve admin note
        response = self.client.get(self.detail_url(self.note_by_admin.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.note_by_admin.refresh_from_db()
        self.assertTrue(self.note_by_admin.is_read)

    def test_retrieve_note_marks_read_for_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        # Retrieve member note
        response = self.client.get(self.detail_url(self.note_by_member.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.note_by_member.refresh_from_db()
        self.assertTrue(self.note_by_member.is_read)

    def test_retrieve_note_non_member_forbidden(self):
        self.client.force_authenticate(user=self.non_member_user)
        response = self.client.get(self.detail_url(self.note_by_member.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_partial_update_note_author(self):
        self.client.force_authenticate(user=self.member_user)
        data = {"content": "Updated content"}
        response = self.client.patch(self.detail_url(self.note_by_member.id), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.note_by_member.refresh_from_db()
        self.assertEqual(self.note_by_member.content, "Updated content")

    def test_partial_update_note_non_author_forbidden(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {"content": "Hacked content"}
        response = self.client.patch(self.detail_url(self.note_by_member.id), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_cannot_access(self):
        self.client.logout()
        # List
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # Create
        response = self.client.post(self.list_create_url, {"content": "Note"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # Retrieve
        response = self.client.get(self.detail_url(self.note_by_member.id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # Patch
        response = self.client.patch(self.detail_url(self.note_by_member.id), {"content": "X"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

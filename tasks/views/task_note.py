from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from drf_spectacular.utils import extend_schema, OpenApiResponse

from tasks.models import TaskNote, Task, TaskAssignment
from tasks.serializers import TaskNoteSerializer
from utils.response import success_response, error_response
from tasks.errors.loader import get_error
from teams.models import TeamMember
from users.permissions import IsAuthenticated


class TaskNoteViewSet(ModelViewSet):
    """
    CRUD operations for TaskNote with read status management.

    Permissions:
    - Only task owner/admin or the assignment member can view notes.
    - Notes created by admins/owners are visible to the assignment member.
    - Notes created by assignment members are visible to admins/owners.
    - When a note is retrieved by the target user, `is_read` is automatically set to True.
    """

    serializer_class = TaskNoteSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """
        Filter notes based on the role of the requesting user:
        - Owner/Admin sees notes created by members.
        - Assigned member sees notes created by owner/admin.
        """
        user = self.request.user
        qs = TaskNote.objects.all()

        # Optionally filter by task_id if provided
        task_id = self.kwargs.get("task_id")
        if task_id:
            try:
                task = Task.objects.get(id=task_id)
            except Task.DoesNotExist:
                return TaskNote.objects.none()

            try:
                membership = TeamMember.objects.get(team=task.team, user=user)
            except TeamMember.DoesNotExist:
                membership = None

            if membership and membership.role in ("owner", "admin"):
                # Admin/Owner sees notes from members
                return qs.filter(task=task).exclude(author__role__in=("owner", "admin"))
            else:
                # Assigned member sees notes from admins/owners
                try:
                    assignment = TaskAssignment.objects.get(task=task, member__user=user)
                except TaskAssignment.DoesNotExist:
                    return TaskNote.objects.none()
                return qs.filter(task=task, assignment=assignment).exclude(author__user=user)

        return qs

    def perform_create(self, serializer):
        """
        Automatically assign author and link task/assignment.
        """
        user = self.request.user
        task_id = self.kwargs.get("task_id")
        if not task_id:
            raise PermissionDenied("task_id is required.")

        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            raise PermissionDenied("Task not found.")

        try:
            membership = TeamMember.objects.get(team=task.team, user=user)
        except TeamMember.DoesNotExist:
            raise PermissionDenied("You are not a member of this task's team.")

        assignment = None
        if membership.role in ("owner", "admin"):
            # Admin/Owner note → assign to all members (optional: first member of task)
            assignments = task.assignments.all()
            assignment = assignments.first() if assignments.exists() else None
        else:
            # Member note → link to their own assignment
            assignment = TaskAssignment.objects.filter(task=task, member__user=user).first()
            if not assignment:
                raise PermissionDenied("You do not have an assignment for this task.")

        serializer.save(
            task=task,
            assignment=assignment,
            author=membership
        )

    def get_object(self):
        """
        Ensure only allowed users can access the note.
        If the note is retrieved by the target user, mark as read.
        """
        obj = super().get_object()
        user = self.request.user

        try:
            membership = TeamMember.objects.get(team=obj.task.team, user=user)
        except TeamMember.DoesNotExist:
            membership = None

        # Admin/Owner sees notes from members
        if membership and membership.role in ("owner", "admin") and obj.author.user != user:
            obj.is_read = True
            obj.save(update_fields=["is_read"])
            return obj

        # Assigned member sees notes from admin/owner
        if obj.assignment and obj.assignment.member.user == user and obj.author.user != user:
            obj.is_read = True
            obj.save(update_fields=["is_read"])
            return obj

        # Author always sees their own note
        if obj.author.user == user:
            return obj

        raise PermissionDenied("You do not have permission to access this note.")

    @extend_schema(
        summary="List notes for a task",
        description="List notes for a task visible to the requesting user.",
        responses={200: TaskNoteSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        notes = self.get_queryset()
        serializer = self.get_serializer(notes, many=True)
        return success_response(serializer.data)

    @extend_schema(
        summary="Retrieve a specific note",
        description="Retrieve a task note if you have access. Marks note as read automatically.",
        responses={200: TaskNoteSerializer()}
    )
    def retrieve(self, request, *args, **kwargs):
        note = self.get_object()
        serializer = self.get_serializer(note)
        return success_response(serializer.data)

    @extend_schema(
        summary="Create a new note for a task",
        description="Create a note linked to a task and optionally an assignment.",
        request=TaskNoteSerializer,
        responses={201: TaskNoteSerializer(), 403: OpenApiResponse(description="Permission denied")}
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return success_response(serializer.data, status=status.HTTP_201_CREATED)
        return error_response(
            error_dict=get_error("TASK_003001", details=serializer.errors),
            status=status.HTTP_400_BAD_REQUEST
        )

    @extend_schema(
        summary="Partial update a note",
        description="Update note content or is_read status. Only author can update.",
        request=TaskNoteSerializer,
        responses={200: TaskNoteSerializer(), 403: OpenApiResponse(description="Permission denied")}
    )
    def partial_update(self, request, *args, **kwargs):
        note = self.get_object()
        # Only author can update
        if note.author.user != request.user:
            raise PermissionDenied("Only author can update this note.")

        serializer = self.get_serializer(note, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return success_response(serializer.data)
        return error_response(
            error_dict=get_error("TASK_003002", details=serializer.errors),
            status=status.HTTP_400_BAD_REQUEST
        )

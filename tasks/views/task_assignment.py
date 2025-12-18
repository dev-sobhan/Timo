from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from drf_spectacular.utils import extend_schema, OpenApiResponse
from tasks.models import TaskAssignment, Task
from tasks.serializers import TaskAssignmentSerializer
from utils.response import success_response, error_response
from tasks.errors.loader import get_error
from teams.models import TeamMember
from users.permissions import IsAuthenticated


class TaskAssignmentViewSet(ModelViewSet):
    """
    TaskAssignment CRUD operations.

    Permissions:
    - Only task owner/admin or assigned member can view or update the assignment.
    - Only task owner/admin can create new assignments for a task.
    """

    serializer_class = TaskAssignmentSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """
        Filter assignments:
        - Members see only their own assignments.
        - Owner/Admin can see all assignments of the task.
        """
        user = self.request.user
        qs = TaskAssignment.objects.all()

        # For list action, filter by task_id if provided
        task_id = self.kwargs.get("task_id")
        if task_id:
            try:
                task = Task.objects.get(id=task_id)
            except Task.DoesNotExist:
                return TaskAssignment.objects.none()

            try:
                membership = TeamMember.objects.get(team=task.team, user=user)
            except TeamMember.DoesNotExist:
                # Non-member sees nothing
                return TaskAssignment.objects.none()

            if membership.role in ("owner", "admin"):
                return qs.filter(task=task)
            else:
                # Only assigned member can see their own assignment
                return qs.filter(task=task, member__user=user)

        return qs

    def perform_create(self, serializer):
        """
        Only task owner/admin can create assignment
        """
        task_id = self.kwargs.get("task_id")
        if not task_id:
            raise PermissionDenied("task_id is required.")

        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            raise PermissionDenied("Task not found.")

        try:
            membership = TeamMember.objects.get(team=task.team, user=self.request.user)
        except TeamMember.DoesNotExist:
            raise PermissionDenied("You are not a member of this task's team.")

        if membership.role not in ("owner", "admin"):
            raise PermissionDenied("Only team owner or admin can create assignment.")

        serializer.save(task=task)

    def get_object(self):
        """
        Ensure that only allowed members can access assignment object
        """
        obj = super().get_object()
        user = self.request.user

        # Owner/Admin of the task team can access all
        try:
            membership = TeamMember.objects.get(team=obj.task.team, user=user)
        except TeamMember.DoesNotExist:
            membership = None

        if membership and membership.role in ("owner", "admin"):
            return obj

        # Only assigned member can access their assignment
        if obj.member.user_id == user.id:
            return obj

        raise PermissionDenied("You do not have permission to access this assignment.")

    @extend_schema(
        summary="List assignments for a task",
        description="List all assignments of a task. Owner/Admin sees all; members see only their assignment.",
        responses={200: TaskAssignmentSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        assignments = self.get_queryset()
        serializer = self.get_serializer(assignments, many=True)
        return success_response(serializer.data)

    @extend_schema(
        summary="Retrieve a specific assignment",
        description="Retrieve assignment details if you have access.",
        responses={200: TaskAssignmentSerializer()}
    )
    def retrieve(self, request, *args, **kwargs):
        assignment = self.get_object()
        serializer = self.get_serializer(assignment)
        return success_response(serializer.data)

    @extend_schema(
        summary="Create a new assignment for a task",
        description="Only team owner/admin can create an assignment.",
        request=TaskAssignmentSerializer,
        responses={201: TaskAssignmentSerializer(), 403: OpenApiResponse(description="Permission denied")}
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return success_response(serializer.data, status=status.HTTP_201_CREATED)
        return error_response(
            error_dict=get_error(key="TASK_001012", details=serializer.errors),
            status=status.HTTP_400_BAD_REQUEST
        )

    @extend_schema(
        summary="Partial update assignment",
        description="Update assignment status, progress, answer or file. Only assigned member or owner/admin.",
        request=TaskAssignmentSerializer,
        responses={200: TaskAssignmentSerializer(), 403: OpenApiResponse(description="Permission denied")}
    )
    def partial_update(self, request, *args, **kwargs):
        assignment = self.get_object()
        serializer = self.get_serializer(assignment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return success_response(serializer.data)
        return error_response(
            error_dict=get_error(key="TASK_001013", details=serializer.errors),
            status=status.HTTP_400_BAD_REQUEST
        )

from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiResponse

from tasks.models import Task
from tasks.serializers import TaskSerializer
from tasks.permissions import IsTaskTeamOwnerOrAdmin,IsTeamOwnerOrAdmin
from teams.models import Team
from users.permissions import IsAuthenticated
from utils.response import success_response, error_response
from tasks.errors.loader import get_error


class TaskViewSet(ModelViewSet):
    """
    Task management API.

    This ViewSet provides APIs to:
    - Create tasks for a team
    - List tasks of a team
    - Retrieve task details
    - Partially update a task

    Access Rules:
    - Only authenticated users can access the endpoints
    - Only team owners or admins can create or list tasks
    - Only team owners or admins can retrieve or update a task
    """

    serializer_class = TaskSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """
        Restrict task visibility to teams where the user is a member.
        Prevents unauthorized access to tasks of other teams.
        """
        return Task.objects.filter(
            team__members__user=self.request.user
        ).select_related("team").distinct()

    def get_permissions(self):
        """
        Dynamically assign permissions based on action.
        """
        permissions = [IsAuthenticated()]

        if self.action in ["retrieve", "partial_update"]:
            permissions.append(IsTaskTeamOwnerOrAdmin())
        elif self.action in ["create", "list"]:
            permissions.append(IsTeamOwnerOrAdmin())

        return permissions

    @extend_schema(
        summary="Create a new task",
        description=(
            "Create a new task for a specific team. "
            "Only team owners or administrators are allowed to create tasks."
        ),
        request=TaskSerializer,
        responses={
            201: OpenApiResponse(
                description="Task created successfully",
                response=TaskSerializer
            ),
            400: OpenApiResponse(
                description="Invalid input data or validation error"
            ),
            403: OpenApiResponse(
                description="Permission denied"
            ),
            404: OpenApiResponse(
                description="Team not found"
            ),
        },
    )
    def create(self, request, *args, **kwargs):
        team_id = self.kwargs.get("team_id")

        if not team_id:
            return error_response(
                error_dict=get_error("TEAM_001004"),
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            team = Team.objects.get(id=team_id)
        except Team.DoesNotExist:
            return error_response(
                error_dict=get_error("TEAM_001005"),
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(
                team=team,
                created_by=team.members.get(user=request.user)
            )
            return success_response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return error_response(
            error_dict=get_error("TASK_001002", details=serializer.errors),
            status=status.HTTP_400_BAD_REQUEST
        )

    @extend_schema(
        summary="List team tasks",
        description=(
            "Retrieve all tasks associated with a specific team. "
            "Only team owners or administrators can access this endpoint."
        ),
        responses={
            200: OpenApiResponse(
                description="Tasks retrieved successfully",
                response=TaskSerializer(many=True)
            ),
            403: OpenApiResponse(
                description="Permission denied"
            ),
            404: OpenApiResponse(
                description="Team not found"
            ),
        },
    )
    def list(self, request, *args, **kwargs):
        team_id = self.kwargs.get("team_id")

        if not team_id:
            return error_response(
                error_dict=get_error("TASK_001007"),
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            team = Team.objects.get(id=team_id)
        except Team.DoesNotExist:
            return error_response(
                error_dict=get_error("TASK_001008"),
                status=status.HTTP_404_NOT_FOUND
            )

        tasks = team.tasks.all()
        serializer = self.get_serializer(tasks, many=True)
        return success_response(serializer.data)

    @extend_schema(
        summary="Retrieve task details",
        description=(
            "Retrieve detailed information of a specific task. "
            "Only team owners or administrators can access this endpoint."
        ),
        responses={
            200: OpenApiResponse(
                description="Task details retrieved successfully",
                response=TaskSerializer
            ),
            403: OpenApiResponse(
                description="Permission denied"
            ),
            404: OpenApiResponse(
                description="Task not found"
            ),
        },
    )
    def retrieve(self, request, *args, **kwargs):
        task = self.get_object()
        serializer = self.get_serializer(task)
        return success_response(serializer.data)

    @extend_schema(
        summary="Update task (partial)",
        description=(
            "Partially update a task fields such as title, description, "
            "status or due date. Only team owners or administrators are allowed."
        ),
        request=TaskSerializer,
        responses={
            200: OpenApiResponse(
                description="Task updated successfully",
                response=TaskSerializer
            ),
            400: OpenApiResponse(
                description="Invalid update data"
            ),
            403: OpenApiResponse(
                description="Permission denied"
            ),
            404: OpenApiResponse(
                description="Task not found"
            ),
        },
    )
    def partial_update(self, request, *args, **kwargs):
        task = self.get_object()
        serializer = self.get_serializer(
            task,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return success_response(serializer.data)

        return error_response(
            error_dict=get_error("TASK_001003", details=serializer.errors),
            status=status.HTTP_400_BAD_REQUEST
        )

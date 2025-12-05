from rest_framework import status, viewsets
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, OpenApiResponse
from users.permissions import IsAuthenticated
from utils.response import success_response, error_response
from teams.errors.loader import get_error
from teams.models import Team, TeamMember
from teams.serializers import TeamSerializer
from teams.permissions import IsTeamOwnerOrAdmin


class TeamViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing teams.

    Supports:
    - GET: Retrieve teams or team details
    - POST: Create a new team (Owner member created automatically)
    - PATCH: Partially update a team (Owner/Admin only)
    - Custom actions: my_teams, public_teams, activate, deactivate
    """

    serializer_class = TeamSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ["get", "post", "patch"]

    def get_queryset(self):
        user = self.request.user
        if self.action == "my_teams":
            return Team.objects.filter(members__user=user)
        elif self.action == "public_teams":
            return Team.objects.filter(is_visible=True, is_active=True)
        return Team.objects.all()

    def get_permissions(self):
        """
        Owner/Admin required for update, partial_update, activate, deactivate.
        """
        permissions = list(self.permission_classes)
        if self.action in ['update', 'partial_update', 'activate', 'deactivate']:
            permissions.append(IsTeamOwnerOrAdmin)
        return (perm() for perm in permissions)

    @extend_schema(
        summary="Create a new team",
        description=(
                "Creates a new team and automatically assigns the authenticated user as the owner. "
                "The request must include required team fields such as name, visibility status, "
                "and optional description. Validation errors are returned if provided data is invalid."
        ),
        request=TeamSerializer,
        responses={
            201: OpenApiResponse(
                description="Team created successfully",
                response=TeamSerializer
            ),
            400: OpenApiResponse(
                description="Invalid team data or validation error",
                response=dict
            )
        }
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            team = serializer.save()
            # Automatically create the owner TeamMember
            TeamMember.objects.create(team=team, user=request.user, role='owner')
            return success_response(serializer.data, status=status.HTTP_201_CREATED)

        return error_response(
            error_dict=get_error("TEAM_001004", details=serializer.errors),
            status=status.HTTP_400_BAD_REQUEST
        )

    @extend_schema(
        summary="Retrieve teams owned or joined by the user",
        description=(
                "Returns a list of all teams where the authenticated user is a member. "
                "Includes teams where user is owner, admin, or regular member."
        ),
        responses={
            200: OpenApiResponse(
                description="List of teams the user is a member of",
                response=TeamSerializer
            )
        }
    )
    @action(detail=False, methods=['get'])
    def my_teams(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return success_response(serializer.data)

    @extend_schema(
        summary="Retrieve public teams",
        description=(
                "Returns a list of all public teams. Public teams are visible to all users and "
                "have both 'is_visible' and 'is_active' set to true. "
                "This endpoint does not require ownership or team membership."
        ),
        responses={
            200: OpenApiResponse(
                description="List of public teams",
                response=TeamSerializer
            )
        }
    )
    @action(detail=False, methods=['get'])
    def public_teams(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return success_response(serializer.data)

    @extend_schema(
        summary="Activate a team",
        description=(
                "Activates a specific team. Only team owners and admins are allowed to perform this action. "
                "Once activated, the team becomes fully functional for its members."
        ),
        responses={
            200: OpenApiResponse(description="Team activated successfully"),
            400: OpenApiResponse(description="Failed to activate team", response=dict),
            404: OpenApiResponse(description="Team not found")
        }
    )
    @action(detail=True, methods=['patch'])
    def activate(self, request, pk: int = None):
        try:
            team = self.get_object()
            team.is_active = True
            team.save(update_fields=['is_active'])
            return success_response({'status': 'Team activated'})
        except Exception as e:
            return error_response(
                error_dict=get_error("TEAM_001005", details=str(e)),
                status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        summary="Deactivate a team",
        description=(
                "Deactivates a specific team, making it unavailable for public or member usage. "
                "Only team owners and admins are authorized to perform this action."
        ),
        responses={
            200: OpenApiResponse(description="Team deactivated successfully"),
            400: OpenApiResponse(description="Failed to deactivate team", response=dict),
            404: OpenApiResponse(description="Team not found")
        }
    )
    @action(detail=True, methods=['patch'])
    def deactivate(self, request, pk: int = None):
        try:
            team = self.get_object()
            team.is_active = False
            team.save(update_fields=['is_active'])
            return success_response({'status': 'Team deactivated'})
        except Exception as e:
            return error_response(
                error_dict=get_error("TEAM_001006", details=str(e)),
                status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        summary="Update team details (partial update)",
        description=(
                "Partially updates team information. Only team owners or admins can update team fields. "
                "Fields not included in the request payload remain unchanged. "
                "Validation errors will be returned if data is invalid."
        ),
        request=TeamSerializer,
        responses={
            200: OpenApiResponse(
                description="Team updated successfully",
                response=TeamSerializer
            ),
            400: OpenApiResponse(
                description="Invalid update data or validation error",
                response=dict
            ),
            404: OpenApiResponse(description="Team not found")
        }
    )
    def partial_update(self, request, *args, **kwargs):
        team = self.get_object()
        serializer = self.get_serializer(team, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return success_response(serializer.data)

        return error_response(
            error_dict=get_error("TEAM_001007", details=serializer.errors),
            status=status.HTTP_400_BAD_REQUEST
        )

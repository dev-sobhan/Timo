from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiResponse
from teams.models import Team, TeamRequest, TeamMember
from teams.serializers import TeamRequestSerializer
from teams.permissions import IsTeamOwnerOrAdmin
from users.permissions import IsAuthenticated
from utils.response import success_response, error_response
from teams.errors.loader import get_error


class TeamMembershipAdminViewSet(ModelViewSet):
    """
    ViewSet to manage membership requests for teams where the authenticated user
    has an administrative role (owner or admin).

    Available actions:
    - list: List all pending requests for all teams where the user is owner/admin
    - list_team_requests: List all pending requests for a specific team
    - accept: Accept a membership request
    - reject: Reject a membership request
    - retrieve: Get details of a specific membership request
    """

    serializer_class = TeamRequestSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """
        Return the queryset depending on the action.
        - list: All pending requests for teams where user is owner/admin
        - list_team_requests: All pending requests for a specific team
        - retrieve/accept/reject: Only requests for teams where user is owner/admin
        """

        if self.action == 'list_team_requests':
            team_id = self.kwargs.get('pk')
            return TeamRequest.objects.filter(team__id=team_id, status='pending')
        my_teams = Team.objects.filter(
            members__user=self.request.user, members__role__in=['owner', 'admin']
        )
        if self.action == 'list':
            return TeamRequest.objects.filter(team__in=my_teams, status='pending')
        # For retrieve/accept/reject, restrict to requests belonging to user's teams
        return TeamRequest.objects.filter(team__in=my_teams)

    def get_permissions(self):
        """
        Return the appropriate permissions depending on the action.

        - list: Authenticated users only
        - other actions: Only team owner or admin
        """
        if self.action == 'list_team_requests':
            return (IsTeamOwnerOrAdmin(),)
        return (IsAuthenticated(),)

    @extend_schema(
        summary="List all pending membership requests for teams where the user is owner/admin",
        description="Retrieve all pending membership requests across all teams where the authenticated user has owner or admin rights.",
        responses={200: OpenApiResponse(description="List of membership requests", response=serializer_class)}
    )
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return success_response(serializer.data)

    @extend_schema(
        summary="List all pending membership requests for a specific team",
        description="Retrieve all pending membership requests for a team identified by `team_id`. "
                    "The user must be owner or admin of that team.",
        responses={200: OpenApiResponse(description="List of membership requests", response=serializer_class)}
    )
    @action(detail=False, methods=['get'], url_path='team/(?P<pk>[^/.]+)')
    def list_team_requests(self, request, pk: int = None):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return success_response(serializer.data)

    @extend_schema(
        summary="Accept a membership request",
        description="Accept a pending membership request. "
                    "The authenticated user must be owner or admin of the target team.",
        responses={200: OpenApiResponse(description="Request successfully accepted", response=serializer_class)}
    )
    @action(detail=True, methods=['delete'])
    def accept(self, request, pk: int = None):
        try:
            instance = self.get_object()
            if instance.team.members.filter(user=request.user, role__in=['owner', 'admin']).exists():
                instance.status = 'accepted'
                instance.save(update_fields=['status'])
                TeamMember.objects.create(team=instance.team, user=request.user)
                return success_response({'status': 'Request accepted'})

            return error_response(
                error_dict=get_error(key="TEAM_001009"),
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return error_response(
                error_dict=get_error(key="TEAM_001010", details=str(e)),
                status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        summary="Reject a membership request",
        description="Reject a pending membership request. "
                    "The authenticated user must be owner or admin of the target team.",
        responses={200: OpenApiResponse(description="Request successfully rejected", response=serializer_class)}
    )
    @action(detail=True, methods=['patch'])
    def reject(self, request, pk: int = None):
        try:
            instance = self.get_object()
            instance.status = 'rejected'
            instance.save(update_fields=['status'])
            return success_response({'status': 'Request rejected'})
        except TeamRequest.DoesNotExist:
            return error_response(
                error_dict=get_error(key="TEAM_001011"),
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return error_response(
                error_dict=get_error(key="TEAM_001012", details=str(e)),
                status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        summary="Retrieve a specific membership request",
        description="Get detailed information about a specific membership request identified by its ID.",
        responses={200: OpenApiResponse(description="Membership request details", response=serializer_class)}
    )
    @action(detail=True, methods=['get'])
    def retrieve(self, request, pk: int = None):
        instance = self.get_object()
        serializer = self.serializer_class(instance)
        return success_response(serializer.data)

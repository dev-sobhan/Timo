from rest_framework.viewsets import ModelViewSet
from teams.serializers import TeamRequestSerializer
from users.permissions import IsAuthenticated
from teams.models import TeamRequest
from utils.response import success_response, error_response
from teams.errors.loader import get_error
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import status


class UserMembershipRequestViewSet(ModelViewSet):
    """
    API endpoints for authenticated users to manage their own team membership requests.

    This ViewSet provides:
      - Creating a new membership request for a team.
      - Listing all membership requests submitted by the user.
      - Retrieving a single membership request belonging to the user.

    Only the authenticated user’s own requests are accessible.
    """

    serializer_class = TeamRequestSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """
        Limit queryset to the authenticated user's membership requests.
        """
        return TeamRequest.objects.filter(user=self.request.user)

    @extend_schema(
        summary="Submit a membership request to a team",
        description=(
                "Creates a new membership request for the authenticated user. "
                "If the user has already sent a request to the same team or the provided "
                "payload is invalid, a validation error will be returned."
        ),
        request=serializer_class,
        responses={
            201: OpenApiResponse(
                description="Membership request submitted successfully",
                response=serializer_class
            ),
            400: OpenApiResponse(
                description="Invalid data or duplicate request",
                response=dict
            )
        }
    )
    def create(self, request, *args, **kwargs):
        """
        Create a new team membership request for the authenticated user.

        Returns:
            201: On successful creation.
            400: If validation fails.
        """
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=request.user)
            return success_response(serializer.data, status=status.HTTP_201_CREATED)

        return error_response(
            error_dict=get_error(key="TEAM_001008", details=serializer.errors),
            status=status.HTTP_400_BAD_REQUEST
        )

    @extend_schema(
        summary="List user’s membership requests",
        description=(
                "Returns a list of all membership requests submitted by the authenticated user. "
                "This endpoint does not show requests submitted by other users."
        ),
        responses={
            200: OpenApiResponse(
                description="List of user’s membership requests",
                response=serializer_class
            )
        }
    )
    def list(self, request, *args, **kwargs):
        """
        Retrieve all membership requests submitted by the authenticated user.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return success_response(serializer.data)

    @extend_schema(
        summary="Retrieve a specific membership request",
        description=(
                "Returns details of a single membership request belonging to the authenticated user. "
                "If the request does not belong to the user or does not exist, an error is returned."
        ),
        responses={
            200: OpenApiResponse(
                description="Membership request details",
                response=serializer_class
            ),
            404: OpenApiResponse(description="Request not found")
        }
    )
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve details of a single membership request for the authenticated user.
        """
        instance = self.get_object()  # Safe due to queryset restriction
        serializer = self.get_serializer(instance)
        return success_response(serializer.data)

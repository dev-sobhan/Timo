from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from drf_spectacular.utils import extend_schema, OpenApiResponse
from users.permissions import IsAuthenticated
from utils.response import success_response, error_response
from users.errors.loader import get_error
from users.serializers.profile import ProfileSerializer


class ProfileViewSet(ModelViewSet):
    """
    API for viewing and updating the authenticated user's profile.
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = ProfileSerializer
    http_method_names = ["get", "patch"]

    def get_object(self):
        """Return the profile of the authenticated user."""
        return self.request.user.profile

    @extend_schema(
        summary="Get authenticated user's profile",
        responses={
            200: OpenApiResponse(
                description="Profile fetched successfully",
                response=ProfileSerializer
            )
        }
    )
    def list(self, request, *args, **kwargs):
        profile = self.get_object()
        serializer = self.get_serializer(profile)
        return success_response(serializer.data)

    @extend_schema(
        summary="Update authenticated user's profile",
        request=ProfileSerializer,
        responses={
            200: OpenApiResponse(
                description="Profile updated successfully",
                response=ProfileSerializer
            ),
            400: OpenApiResponse(
                description="Validation error",
                response=dict
            )
        }
    )
    def partial_update(self, request, *args, **kwargs):
        profile = self.get_object()
        serializer = self.get_serializer(profile, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return success_response(serializer.data)

        return error_response(
            error_dict=get_error("USR_001003", details=serializer.errors),
            status=status.HTTP_400_BAD_REQUEST
        )

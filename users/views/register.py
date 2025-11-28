from rest_framework import status
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.response import Response
from users.permissions import AllowOnlyUnauthenticated
from users.serializers import RegisterSerializer
from users.errors.loader import get_error
from utils.response import success_response, error_response


class RegisterApiView(APIView):
    """
    API endpoint for user registration.

    This view allows **unauthenticated users** to create a new account.
    Registration includes validation of required fields and password hashing.
    """

    permission_classes = (AllowOnlyUnauthenticated,)

    @extend_schema(
        summary="Register a new user",
        description=(
            "Register a new user account.\n\n"
            "The endpoint expects 'full_name', 'email', and 'password'.\n"
            "Returns a standardized success response if registration succeeds.\n"
            "If validation fails, returns standardized error response with details."
        ),
        request=RegisterSerializer,
        responses={
            201: OpenApiResponse(
                response={
                    "success": True,
                    "data": {"id": "integer", "email": "string"},
                    "error": None
                },
                description="User registered successfully"
            ),
            400: OpenApiResponse(
                response={
                    "success": False,
                    "data": None,
                    "error": {
                        "code": "USR_001001",
                        "message": "User registration validation failed.",
                        "details": {"field_name": ["error message"]}
                    }
                },
                description="Validation error or other registration errors"
            )
        }
    )
    def post(self, request) -> Response:
        """
        Handle POST request to register a new user.

        Args:
            request (Request): DRF request object containing registration data.

        Returns:
            Response: DRF Response object with standardized success or error structure.
        """
        serializer = RegisterSerializer(data=request.data)

        # Validate input data
        if serializer.is_valid():
            user = serializer.save()  # Save user with hashed password
            # Return standardized success response
            return success_response(
                data={"id": user.id, "email": user.email},
                status=status.HTTP_201_CREATED
            )

        # If validation fails, return standardized error response with serializer errors
        return error_response(
            error_dict=get_error(
                key="USR_001001",
                details=serializer.errors
            ),
            status=status.HTTP_400_BAD_REQUEST
        )

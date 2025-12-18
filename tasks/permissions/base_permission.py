from rest_framework.permissions import BasePermission
from tasks.errors.loader import get_error


class BaseCustomPermission(BasePermission):
    """
    Base permission that allows sending standardized error responses
    when permission is denied.
    """
    message = None
    error_code = None

    def has_permission(self, request, view):
        """
        Default implementation, should be overridden in child classes.
        """
        return True

    def deny(self):
        """
        Return the standardized error dict for this permission.
        """
        if self.error_code:
            return get_error(self.error_code)
        return {"code": "PERMISSION_DENIED", "message": "Access denied"}

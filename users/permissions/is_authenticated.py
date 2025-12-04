from .base_permission import BaseCustomPermission


class IsAuthenticated(BaseCustomPermission):
    error_code = "USR_001002"

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            self.message = self.deny()
            return False
        return True

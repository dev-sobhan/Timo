from .base_permission import BaseCustomPermission


class AllowOnlyUnauthenticated(BaseCustomPermission):
    error_code = "USR_001000"

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            self.message = self.deny()
            return False
        return True

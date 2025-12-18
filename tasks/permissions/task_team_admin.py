from .base_permission import BaseCustomPermission
from teams.models import TeamMember


class IsTaskTeamOwnerOrAdmin(BaseCustomPermission):
    """
    Permission to allow only Team Owner or Admin to perform actions on a Task instance.
    """

    error_code = "TASK_001000"  # Unique error code for permission denial

    def has_object_permission(self, request, view, obj):
        """
        Check if the authenticated user is Owner or Admin of the team instance (obj).
        """
        try:
            membership = obj.team.members.get(user=request.user)
        except TeamMember.DoesNotExist:
            self.error_code = "TASK_001000"
            self.message = self.deny()
            return False

        if membership.role not in ['owner', 'admin']:
            self.error_code = "TASK_001001"
            self.message = self.deny()
            return False

        return True

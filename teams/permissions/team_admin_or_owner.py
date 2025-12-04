from users.permissions.base_permission import BaseCustomPermission
from teams.models import TeamMember


class IsTeamOwnerOrAdmin(BaseCustomPermission):
    """
    Permission to allow only Team Owner or Admin to perform actions on a Team instance.
    """

    error_code = "TEAM_001001"  # Unique error code for permission denial

    def has_object_permission(self, request, view, obj):
        """
        Check if the authenticated user is Owner or Admin of the team instance (obj).
        """
        if not request.user.is_authenticated:
            self.error_code = "TEAM_001001"
            self.message = self.deny()
            return False

        try:
            membership = TeamMember.objects.get(team=obj, user=request.user)
        except TeamMember.DoesNotExist:
            self.error_code = "TEAM_001002"
            self.message = self.deny()
            return False

        if membership.role not in ['owner', 'admin']:
            self.error_code = "TEAM_001003"
            self.message = self.deny()
            return False

        return True

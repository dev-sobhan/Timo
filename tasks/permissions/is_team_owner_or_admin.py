from .base_permission import BaseCustomPermission
from teams.models import TeamMember


class IsTeamOwnerOrAdmin(BaseCustomPermission):
    def has_permission(self, request, view):
        """
        Permission check for list/create actions where no object exists.
        """
        if not request.user or not request.user.is_authenticated:
            self.message = self.deny()
            return False

        team_id = view.kwargs.get("team_id")

        # If no team context, deny explicitly
        if not team_id:
            self.error_code = "TASK_001009"
            self.message = self.deny()
            return False

        try:
            membership = TeamMember.objects.get(
                team_id=team_id,
                user=request.user
            )
        except TeamMember.DoesNotExist:
            self.error_code = "TASK_001010"
            self.message = self.deny()
            return False

        if membership.role not in ("owner", "admin"):
            self.error_code = "TASK_001011"
            self.message = self.deny()
            return False

        return True

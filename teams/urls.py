from django.urls import path
from .views import TeamViewSet, UserMembershipRequestViewSet, TeamMembershipAdminViewSet

app_name = 'teams'

urlpatterns = [

    path(
        "membership/requests/admin/",
        TeamMembershipAdminViewSet.as_view({"get": "list"}),
        name="membership_request_list"
    ),

    # # List all pending requests for a specific team
    path(
        "membership/teams/<int:pk>/requests/admin/",
        TeamMembershipAdminViewSet.as_view({"get": "list_team_requests"}),
        name="membership_request_admin_team"
    ),

    # Retrieve or accept a specific membership request
    path(
        "membership/request/admin/<int:pk>/",
        TeamMembershipAdminViewSet.as_view({"get": "retrieve", "patch": "accept", "delete": "reject"}),
        name="membership_request_detail_admin"
    ),

    # user membership
    path("membership/request/", UserMembershipRequestViewSet.as_view({
        "get": "list",
        "post": "create"
    }), name="membership_request"),
    path("membership/request/<int:pk>/", UserMembershipRequestViewSet.as_view({
        "get": "retrieve",
    }), name="membership_request_detail"),

    # Public teams
    path("list/", TeamViewSet.as_view({"get": "public_teams"}), name="team-public-list"),

    # My teams and create
    path("my/", TeamViewSet.as_view({"get": "my_teams"}), name="team-my-teams"),
    path("", TeamViewSet.as_view({"get": "list", "post": "create"}), name="team-list"),

    # Team detail + update + activate/deactivate
    path("<int:pk>/", TeamViewSet.as_view({"get": "retrieve", "patch": "partial_update"}), name="team-detail"),
    path("<int:pk>/activate/", TeamViewSet.as_view({"patch": "activate"}), name="team-activate"),
    path("<int:pk>/deactivate/", TeamViewSet.as_view({"patch": "deactivate"}), name="team-deactivate"),
]

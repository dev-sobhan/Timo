from django.urls import path
from .views import TeamViewSet, UserMembershipRequestViewSet

app_name = 'teams'

urlpatterns = [
    # membership
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

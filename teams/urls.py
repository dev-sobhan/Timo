from django.urls import path
from .views import TeamViewSet

app_name = 'teams'

urlpatterns = [
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

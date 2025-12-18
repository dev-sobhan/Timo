from django.urls import path
from .views import TaskViewSet

app_name = 'tasks'

urlpatterns = [
    path("teams/<int:team_id>/", TaskViewSet.as_view({
        "get": "list",
        "post": "create",
    }), name="team_tasks"),
    path("<int:pk>/", TaskViewSet.as_view({
        "get": "retrieve",
        "patch": "partial_update",
    }), name="task")
]

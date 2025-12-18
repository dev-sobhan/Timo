from django.urls import path
from .views import TaskViewSet, TaskAssignmentViewSet, TaskNoteViewSet

app_name = 'tasks'

urlpatterns = [
    path("tasks/<int:task_id>/notes/", TaskNoteViewSet.as_view({
        "get": "list",
        "post": "create",
    }), name="task_notes"),

    path("notes/<int:pk>/", TaskNoteViewSet.as_view({
        "get": "retrieve",
        "patch": "partial_update",
    }), name="task_note_detail"),
    
    path("tasks/<int:task_id>/assignments/", TaskAssignmentViewSet.as_view({
        "get": "list",
        "post": "create",
    }), name="task_assignments"),
    path("assignments/<int:pk>/", TaskAssignmentViewSet.as_view({
        "get": "retrieve",
        "patch": "partial_update",
    }), name="task_assignment_detail"),
    path("teams/<int:team_id>/", TaskViewSet.as_view({
        "get": "list",
        "post": "create",
    }), name="team_tasks"),
    path("<int:pk>/", TaskViewSet.as_view({
        "get": "retrieve",
        "patch": "partial_update",
    }), name="task"),
]

from django.db import models


def task_file_upload_path(instance, filename):
    return f"tasks/{instance.team.id}/{instance.id}/{filename}"


class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    team = models.ForeignKey(
        to="teams.Team",
        on_delete=models.CASCADE,
        related_name="tasks"
    )

    is_team_task = models.BooleanField(default=False)
    file = models.FileField(upload_to=task_file_upload_path, blank=True, null=True)

    created_by = models.ForeignKey(
        to='teams.TeamMember',
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_tasks"
    )

    STATUS_CHOICES = (
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("cancelled", "Cancelled"),
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="active"
    )

    due_date = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

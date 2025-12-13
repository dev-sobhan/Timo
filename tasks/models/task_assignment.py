from django.db import models
from .task import Task


def task_assignment_file_upload_path(instance, filename):
    return f"tasks/{instance.task.team.id}/{instance.task.id}/{instance.id}/{filename}"


class TaskAssignment(models.Model):
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="assignments"
    )

    member = models.ForeignKey(
        to='teams.TeamMember',
        on_delete=models.CASCADE,
        related_name="task_assignments"
    )

    STATUS_CHOICES = (
        ("assigned", "Assigned"),
        ("in_progress", "In Progress"),
        ("done", "Done"),
        ("blocked", "Blocked"),
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="assigned"
    )

    progress = models.PositiveSmallIntegerField(
        default=0,
        help_text="0-100 progress percent"
    )
    answer = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to=task_assignment_file_upload_path, blank=True, null=True)

    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

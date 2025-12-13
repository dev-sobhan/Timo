from django.db import models
from .task import Task
from .task_assignment import TaskAssignment


class TaskNote(models.Model):
    task = models.ForeignKey(
        to=Task,
        on_delete=models.CASCADE,
        related_name="notes"
    )

    assignment = models.ForeignKey(
        to=TaskAssignment,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notes"
    )

    author = models.ForeignKey(
        to='teams.TeamMember',
        on_delete=models.CASCADE
    )
    is_read = models.BooleanField(default=False)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

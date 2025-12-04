from django.db import models
from django.contrib.auth import get_user_model
from .team import Team

User = get_user_model()


class TeamRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    )

    team = models.ForeignKey(
        Team,
        related_name="requests",
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        User,
        related_name="team_requests",
        on_delete=models.CASCADE
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    message = models.TextField(
        blank=True,
        null=True,
        help_text="User explanation about why they want to join the team."
    )

    file = models.FileField(
        upload_to="team_requests/resumes/%Y/%m/%d/",
        blank=True,
        null=True
    )

    note = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('team', 'user')
        ordering = ['-created_at']

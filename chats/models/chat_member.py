from django.db import models
from django.contrib.auth import get_user_model
from .chat import Chat

User = get_user_model()


class ChatMember(models.Model):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"

    ROLE_CHOICES = (
        (OWNER, "Owner"),
        (ADMIN, "Admin"),
        (MEMBER, "Member"),
    )

    chat = models.ForeignKey(
        Chat,
        on_delete=models.CASCADE,
        related_name="members",
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="chat_memberships",
    )

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default=MEMBER,
    )

    is_muted = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "chat_member"
        unique_together = ("chat", "user")
        indexes = [
            models.Index(fields=["chat", "user"]),
            models.Index(fields=["user"]),
        ]


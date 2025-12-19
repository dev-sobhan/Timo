from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Chat(models.Model):
    PRIVATE = "private"
    GROUP = "group"

    CHAT_TYPE_CHOICES = (
        (PRIVATE, "Private"),
        (GROUP, "Group"),
    )

    type = models.CharField(
        max_length=10,
        choices=CHAT_TYPE_CHOICES,
        db_index=True,
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_chats",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "chat"
        ordering = ("-created_at",)

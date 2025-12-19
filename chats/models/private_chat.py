from django.contrib.auth import get_user_model
from django.db import models

from .chat import Chat

User = get_user_model()


class PrivateChat(models.Model):
    chat = models.OneToOneField(
        Chat,
        on_delete=models.CASCADE,
        related_name="private",
    )

    user1 = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="private_chats_as_user1",
    )

    user2 = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="private_chats_as_user2",
    )

    class Meta:
        db_table = "private_chat"
        constraints = [
            models.UniqueConstraint(
                fields=["user1", "user2"],
                name="unique_private_chat_pair",
            )
        ]

    def save(self, *args, **kwargs):
        # enforce user1.id < user2.id to avoid duplication
        if self.user1_id > self.user2_id:
            self.user1, self.user2 = self.user2, self.user1
        super().save(*args, **kwargs)

from django.db import models
from .chat import Chat


class GroupChat(models.Model):
    chat = models.OneToOneField(
        Chat,
        on_delete=models.CASCADE,
        related_name="group",
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    avatar = models.ImageField(
        upload_to="chat/groups/avatars/",
        blank=True,
        null=True,
    )

    class Meta:
        db_table = "group_chat"


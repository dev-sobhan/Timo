from django.db.models.signals import post_save
from django.dispatch import receiver
from teams.models import Team
from chats.models import Chat, GroupChat, ChatMember


@receiver(post_save, sender=Team)
def create_group_chat_for_team(sender, instance: Team, created, **kwargs):
    if created:
        chat = Chat.objects.create(type=Chat.GROUP, created_by=None)
        GroupChat.objects.create(
            chat=chat,
            title=instance.title,
            description=instance.description or ""
        )
        owner_member = instance.members.filter(role="owner").first()
        if owner_member:
            ChatMember.objects.create(chat=chat, user=owner_member.user, role=ChatMember.OWNER)

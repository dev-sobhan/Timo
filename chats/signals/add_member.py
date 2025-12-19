from django.db.models.signals import post_save
from django.dispatch import receiver
from teams.models import TeamMember
from chats.models import GroupChat, ChatMember


@receiver(post_save, sender=TeamMember)
def add_team_member_to_group(sender, instance: TeamMember, created, **kwargs):
    if created:
        try:
            group_chat = GroupChat.objects.get(title=instance.team.title)
        except GroupChat.DoesNotExist:
            return

        if not ChatMember.objects.filter(chat=group_chat.chat, user=instance.user).exists():
            ChatMember.objects.create(chat=group_chat.chat, user=instance.user, role=ChatMember.MEMBER)

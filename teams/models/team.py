from django.db import models


class Team(models.Model):
    STATUS_CHOICES = (
        ('verified', 'Verified'),
        ('pending_verification', 'Pending Verification'),
        ('rejected', 'Rejected'),
        ('not_required', 'Not Required'),
    )

    title = models.CharField(max_length=250)
    description = models.TextField(blank=True, null=True)
    is_visible = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    image = models.ImageField(blank=True, null=True, upload_to="teams/%y/%m/%d")

    status = models.CharField(
        max_length=32,
        choices=STATUS_CHOICES,
        default='not_required'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


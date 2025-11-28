from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, max_length=100)

    phone = models.CharField(max_length=20, blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)  # panel access
    is_superuser = models.BooleanField(default=False)

    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        SUB_ADMIN = 'sub_admin', 'Sub Admin'
        USER = 'user', 'User'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.USER
    )

    # timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ("full_name",)

    objects = UserManager()


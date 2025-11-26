from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):

    def normalize_email(self, email):
        """Normalize the email address."""
        return super().normalize_email(email)

    def create_user(self, email, full_name, password=None, **extra_fields):
        """
        Create and return a regular user.
        """

        if not email:
            raise ValueError(_("Email is required"))

        if not full_name:
            raise ValueError(_("Full name is required"))

        email = self.normalize_email(email)

        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_verified", False)
        extra_fields.setdefault("role", "user")

        user = self.model(
            email=email,
            full_name=full_name,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name, password=None, **extra_fields):
        """
        Create and return a superuser with admin privileges.
        """

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_verified", True)
        extra_fields.setdefault("role", "admin")

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True"))

        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True"))

        if extra_fields.get("role") != "admin":
            raise ValueError(_("Superuser must have role='admin'"))

        return self.create_user(email, full_name, password, **extra_fields)

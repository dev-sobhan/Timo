from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "full_name",
            "email",
            "is_verify",
            "role",
            "created_at",
            "update_at",
        )
        read_only_fields = ("id", "is_verify", "role", "created_at", "update_at")

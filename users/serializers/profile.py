from rest_framework import serializers
from users.models import Profile
from .user import UserSerializer


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Profile
        fields = [
            "user",
            "image",
            "cover_image",
            "bio",
            "job_title",
            "phone",
            "location",
            "birth_date",
            "website",
            "linkedin",
            "github",
            "instagram",
        ]

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", None)
        if user_data:
            user = instance.user
            user.full_name = user_data.get("full_name", user.full_name)
            user.save()

        return super().update(instance, validated_data)

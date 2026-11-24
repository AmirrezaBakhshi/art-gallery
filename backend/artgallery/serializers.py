from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from .models import Gallary, Item, TargetFile, contains_number


class ItemSerializer(serializers.ModelSerializer):
    gallary_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Item
        fields = (
            "id", "gallary_id", "target_index", "target_image", "target_data",
            "title", "description", "audio", "audio_name",
            "augmented_video", "extra_video",
        )
        read_only_fields = ("id", "gallary_id")


class GallarySerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, min_length=8)

    class Meta:
        model = Gallary
        fields = (
            "id", "username", "password", "name", "email", "image",
            "address", "contact", "description",
        )
        read_only_fields = ("id", "username", "email")

    def validate_password(self, value):
        if not contains_number(value):
            raise serializers.ValidationError("Your password must contain at least one digit.")
        return value

    def create(self, validated_data):
        raw_password = validated_data.pop("password", None)
        if not raw_password:
            raise serializers.ValidationError({"password": "A password is required."})
        validated_data["password"] = make_password(raw_password)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        raw_password = validated_data.pop("password", None)
        if raw_password:
            instance.password = make_password(raw_password)
        return super().update(instance, validated_data)


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = Gallary
        fields = ("id", "username", "password", "name", "email", "image",
                  "address", "contact", "description")
        read_only_fields = ("id",)

    def validate_password(self, value):
        if not contains_number(value):
            raise serializers.ValidationError("Your password must contain at least one digit.")
        return value

    def create(self, validated_data):
        from datetime import timedelta
        from django.conf import settings
        from django.utils import timezone
        from secrets import token_urlsafe
        from .authentication import token_digest
        validated_data["password"] = make_password(validated_data["password"])
        raw_token = token_urlsafe(32)
        validated_data["api_token"] = token_digest(raw_token)
        validated_data["api_token_expires_at"] = timezone.now() + timedelta(days=settings.GALLERY_SESSION_TTL_DAYS)
        gallery = Gallary.objects.create(**validated_data)
        gallery._issued_token = raw_token
        return gallery


class TargetFileSerializer(serializers.ModelSerializer):
    gallary_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = TargetFile
        fields = ("id", "gallary_id", "file")
        read_only_fields = ("id",)

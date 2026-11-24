from pathlib import Path

from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from .models import Gallary, Item, TargetFile, contains_number


class ItemSerializer(serializers.ModelSerializer):
    gallary_id = serializers.IntegerField(read_only=True)

    MAX_IMAGE_BYTES = 10 * 1024 * 1024
    MAX_AUDIO_BYTES = 25 * 1024 * 1024
    MAX_VIDEO_BYTES = 100 * 1024 * 1024
    AUDIO_EXTENSIONS = {".mp3", ".wav", ".ogg", ".m4a", ".aac"}
    VIDEO_EXTENSIONS = {".mp4", ".webm", ".mov", ".m4v"}

    def _validate_upload(self, value, *, max_bytes, extensions=None):
        if not value:
            return value
        if value.size > max_bytes:
            raise serializers.ValidationError(
                f"File exceeds the maximum allowed size of {max_bytes // (1024 * 1024)} MB."
            )
        if extensions and Path(value.name).suffix.lower() not in extensions:
            raise serializers.ValidationError("Unsupported file extension.")
        return value

    def validate_target_image(self, value):
        return self._validate_upload(value, max_bytes=self.MAX_IMAGE_BYTES)

    def validate_audio(self, value):
        return self._validate_upload(value, max_bytes=self.MAX_AUDIO_BYTES, extensions=self.AUDIO_EXTENSIONS)

    def validate_augmented_video(self, value):
        return self._validate_upload(
            value, max_bytes=self.MAX_VIDEO_BYTES,
            extensions=self.VIDEO_EXTENSIONS | {".jpg", ".jpeg", ".png", ".webp"}
        )

    def validate_extra_video(self, value):
        return self._validate_upload(value, max_bytes=self.MAX_VIDEO_BYTES, extensions=self.VIDEO_EXTENSIONS)

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

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get("request")
        user = getattr(request, "user", None)
        include_private = self.context.get("include_private", False)
        is_owner = bool(user and getattr(user, "is_authenticated", False) and user.pk == instance.pk)
        if not (include_private or is_owner):
            for field in ("email", "address", "contact"):
                data.pop(field, None)
        return data

    def validate_image(self, value):
        if value and value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("Gallery profile images must not exceed 5 MB.")
        return value

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

    def validate_image(self, value):
        if value and value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("Gallery profile images must not exceed 5 MB.")
        return value

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

    def validate_file(self, value):
        # Target assets may be application-specific binary formats; cap size without
        # guessing a format allowlist that could break legitimate gallery workflows.
        if value and value.size > 50 * 1024 * 1024:
            raise serializers.ValidationError("Target files must not exceed 50 MB.")
        return value

    class Meta:
        model = TargetFile
        fields = ("id", "gallary_id", "file")
        read_only_fields = ("id",)

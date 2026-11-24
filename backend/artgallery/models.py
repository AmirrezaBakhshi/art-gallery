from django.core.exceptions import ValidationError
from django.db import models


def contains_number(value):
    return any(character.isdigit() for character in value)


def numberValidator(password):
    # Retained for historical migration imports; new passwords are validated by the API serializer.
    if not contains_number(password):
        raise ValidationError("Your password must contain at least 1 digit")


class Gallary(models.Model):
    username = models.CharField(max_length=50, unique=True)
    # Passwords are stored as Django password hashes, never as plaintext.
    password = models.CharField(max_length=128)
    # SHA-256 digest of the bearer token; the raw token is only returned once.
    api_token = models.CharField(max_length=64, unique=True, null=True, blank=True)
    api_token_expires_at = models.DateTimeField(null=True, blank=True)
    name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    image = models.ImageField(null=True, blank=True, upload_to="gallery_profile/")
    address = models.TextField(blank=True, default="")
    contact = models.TextField(blank=True, default="")
    description = models.TextField(blank=True, default="")

    @property
    def is_authenticated(self):
        """Allow a gallery account to act as the authenticated DRF principal."""
        return True

    def __str__(self):
        return self.name


class Item(models.Model):
    gallary = models.ForeignKey(
        Gallary, on_delete=models.CASCADE, related_name="items",
        null=True, blank=True,
    )
    target_index = models.IntegerField(default=0)
    target_image = models.ImageField(upload_to="target_images/", null=True, blank=True)
    target_data = models.JSONField(null=True, blank=True)
    title = models.TextField()
    description = models.TextField(blank=True)
    audio = models.FileField(upload_to="audios/", null=True, blank=True)
    audio_name = models.TextField(blank=True)
    augmented_video = models.FileField(upload_to="augmented_images_or_videos/", null=True, blank=True)
    extra_video = models.FileField(upload_to="extra_videos/", null=True, blank=True)

    def __str__(self):
        return self.title


class TargetFile(models.Model):
    gallary = models.ForeignKey(
        Gallary, on_delete=models.CASCADE, related_name="target_files",
        null=True, blank=True,
    )
    file = models.FileField(upload_to="target_file/", null=True, blank=True)

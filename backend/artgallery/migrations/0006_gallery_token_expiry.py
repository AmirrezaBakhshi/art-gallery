from datetime import timedelta

from django.db import migrations, models
from django.utils import timezone


def expire_existing_tokens(apps, schema_editor):
    Gallery = apps.get_model("artgallery", "Gallary")
    expires_at = timezone.now() + timedelta(days=14)
    Gallery.objects.filter(api_token__isnull=False).update(api_token_expires_at=expires_at)


class Migration(migrations.Migration):
    dependencies = [("artgallery", "0005_hash_legacy_credentials")]

    operations = [
        migrations.AddField(
            model_name="gallary",
            name="api_token_expires_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.RunPython(expire_existing_tokens, migrations.RunPython.noop),
    ]

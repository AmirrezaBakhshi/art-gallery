import hashlib
import re

from django.contrib.auth.hashers import identify_hasher, make_password
from django.db import migrations


def hash_legacy_credentials(apps, schema_editor):
    Gallery = apps.get_model("artgallery", "Gallary")
    for gallery in Gallery.objects.all().iterator():
        password = gallery.password or ""
        try:
            identify_hasher(password)
        except ValueError:
            if password:
                gallery.password = make_password(password)

        token = gallery.api_token or ""
        if token and not re.fullmatch(r"[0-9a-f]{64}", token):
            gallery.api_token = hashlib.sha256(token.encode("utf-8")).hexdigest()

        gallery.save(update_fields=["password", "api_token"])


class Migration(migrations.Migration):
    dependencies = [("artgallery", "0004_gallery_foreign_keys")]

    operations = [migrations.RunPython(hash_legacy_credentials, migrations.RunPython.noop)]

from django.db import migrations, models
import django.db.models.deletion


def attach_existing_gallery_relations(apps, schema_editor):
    Item = apps.get_model("artgallery", "Item")
    Gallery = apps.get_model("artgallery", "Gallary")
    gallery_ids = set(Gallery.objects.values_list("id", flat=True))
    for item in Item.objects.all().only("id", "gallary_id"):
        if item.gallary_id in gallery_ids:
            Item.objects.filter(pk=item.pk).update(gallery_owner_id=item.gallary_id)


class Migration(migrations.Migration):

    dependencies = [
        ("artgallery", "0003_gallery_authentication"),
    ]

    operations = [
        migrations.AddField(
            model_name="item",
            name="gallery_owner",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                related_name="items", to="artgallery.gallary",
            ),
        ),
        migrations.RunPython(attach_existing_gallery_relations, migrations.RunPython.noop),
        migrations.RemoveField(model_name="item", name="gallary_id"),
        migrations.RenameField(model_name="item", old_name="gallery_owner", new_name="gallary"),
        migrations.AddField(
            model_name="targetfile",
            name="gallary",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                related_name="target_files", to="artgallery.gallary",
            ),
        ),
    ]

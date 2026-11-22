from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("artgallery", "0002_rename_gallery_id_item_gallary_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="gallary",
            name="password",
            field=models.CharField(max_length=128),
        ),
        migrations.AddField(
            model_name="gallary",
            name="api_token",
            field=models.CharField(blank=True, max_length=64, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name="item",
            name="gallary_id",
            field=models.IntegerField(db_index=True),
        ),
        migrations.AlterField(
            model_name="gallary",
            name="image",
            field=models.ImageField(blank=True, null=True, upload_to="gallery_profile/"),
        ),
        migrations.AlterField(
            model_name="item",
            name="target_image",
            field=models.ImageField(blank=True, null=True, upload_to="target_images/"),
        ),
        migrations.AlterField(
            model_name="item",
            name="target_data",
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="item",
            name="audio",
            field=models.FileField(blank=True, null=True, upload_to="audios/"),
        ),
        migrations.AlterField(
            model_name="item",
            name="augmented_video",
            field=models.FileField(blank=True, null=True, upload_to="augmented_images_or_videos/"),
        ),
        migrations.AlterField(
            model_name="item",
            name="extra_video",
            field=models.FileField(blank=True, null=True, upload_to="extra_videos/"),
        ),
        migrations.AlterField(
            model_name="targetfile",
            name="file",
            field=models.FileField(blank=True, null=True, upload_to="target_file/"),
        ),
    ]

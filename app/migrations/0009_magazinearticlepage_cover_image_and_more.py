# Generated by Django 4.1 on 2022-09-05 14:13

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0008_cmsimage_cmsdocument_imagerendition"),
    ]

    operations = [
        migrations.AddField(
            model_name="magazinearticlepage",
            name="cover_image",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="app.cmsimage",
            ),
        ),
        migrations.AddField(
            model_name="magazinearticlepage",
            name="short_description",
            field=models.CharField(default="", max_length=300),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="topichomepage",
            name="short_description",
            field=models.CharField(default=" ", max_length=300),
            preserve_default=False,
        ),
    ]
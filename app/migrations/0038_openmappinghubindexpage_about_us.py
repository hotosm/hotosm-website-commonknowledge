# Generated by Django 4.1.3 on 2022-11-24 11:11

import wagtail.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0037_remove_magazinesection_featured_image_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="openmappinghubindexpage",
            name="about_us",
            field=wagtail.fields.RichTextField(blank=True, max_length=1500, null=True),
        ),
    ]
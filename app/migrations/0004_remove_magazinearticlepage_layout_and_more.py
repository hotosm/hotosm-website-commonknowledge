# Generated by Django 4.1 on 2022-08-17 10:18

import wagtail.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0003_alter_homepage_layout_sitebannersetting"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="magazinearticlepage",
            name="layout",
        ),
        migrations.AddField(
            model_name="magazinearticlepage",
            name="article",
            field=wagtail.fields.RichTextField(default=""),
            preserve_default=False,
        ),
    ]

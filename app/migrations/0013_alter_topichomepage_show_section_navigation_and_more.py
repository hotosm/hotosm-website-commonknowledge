# Generated by Django 4.1.1 on 2022-09-29 10:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0012_articlepage_eventpage_hotosmtag_personpage_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="topichomepage",
            name="show_section_navigation",
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name="topicpage",
            name="show_section_navigation",
            field=models.BooleanField(default=True),
        ),
    ]

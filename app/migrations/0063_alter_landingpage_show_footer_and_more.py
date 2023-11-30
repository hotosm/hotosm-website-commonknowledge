# Generated by Django 4.1.3 on 2023-04-17 18:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0062_alter_user_page"),
    ]

    operations = [
        migrations.AlterField(
            model_name="landingpage",
            name="show_footer",
            field=models.BooleanField(blank=True, default=True, null=True),
        ),
        migrations.AlterField(
            model_name="landingpage",
            name="show_navbar",
            field=models.BooleanField(blank=True, default=True, null=True),
        ),
        migrations.AlterField(
            model_name="landingpage",
            name="show_title",
            field=models.BooleanField(blank=True, default=True, null=True),
        ),
    ]
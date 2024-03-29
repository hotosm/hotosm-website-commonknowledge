# Generated by Django 4.1.3 on 2022-12-01 12:57

import modelcluster.contrib.taggit
import wagtail.blocks
import wagtail.fields
import wagtail.images.blocks
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0049_country_non_unique_codes_and_landing_page_theme"),
    ]

    operations = [
        migrations.AddField(
            model_name="personpage",
            name="email",
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AddField(
            model_name="personpage",
            name="linkedin_url",
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="personpage",
            name="osm_username",
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
        migrations.AddField(
            model_name="personpage",
            name="twitter_username",
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
        migrations.AddField(
            model_name="personpage",
            name="website",
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="personpage",
            name="category",
            field=modelcluster.contrib.taggit.ClusterTaggableManager(
                blank=True,
                help_text="Group people by different categories, and they'll show up together in the staff section. This will also display on the person's profile page.",
                through="app.TaggedPerson",
                to="app.PersonType",
                verbose_name="Category",
            ),
        ),
        migrations.AlterField(
            model_name="personpage",
            name="role",
            field=models.CharField(
                blank=True,
                help_text="Role in the HOTOSM/OSM ecosystem. E.g. 'Executive Director of HOTOSM'",
                max_length=1000,
                null=True,
                verbose_name="Role / job title",
            ),
        ),
    ]

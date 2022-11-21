# Generated by Django 4.1.3 on 2022-11-14 19:21

import django.contrib.gis.db.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0030_articlepage_related_countries_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="articlepage",
            name="coordinates",
            field=django.contrib.gis.db.models.fields.PointField(
                blank=True, null=True, srid=4326
            ),
        ),
        migrations.AddField(
            model_name="articlepage",
            name="geographical_location",
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name="eventpage",
            name="coordinates",
            field=django.contrib.gis.db.models.fields.PointField(
                blank=True, null=True, srid=4326
            ),
        ),
        migrations.AddField(
            model_name="eventpage",
            name="geographical_location",
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name="opportunitypage",
            name="coordinates",
            field=django.contrib.gis.db.models.fields.PointField(
                blank=True, null=True, srid=4326
            ),
        ),
        migrations.AddField(
            model_name="opportunitypage",
            name="geographical_location",
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name="organisationpage",
            name="coordinates",
            field=django.contrib.gis.db.models.fields.PointField(
                blank=True, null=True, srid=4326
            ),
        ),
        migrations.AddField(
            model_name="organisationpage",
            name="geographical_location",
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name="personpage",
            name="coordinates",
            field=django.contrib.gis.db.models.fields.PointField(
                blank=True, null=True, srid=4326
            ),
        ),
        migrations.AddField(
            model_name="personpage",
            name="geographical_location",
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name="projectpage",
            name="coordinates",
            field=django.contrib.gis.db.models.fields.PointField(
                blank=True, null=True, srid=4326
            ),
        ),
        migrations.AddField(
            model_name="projectpage",
            name="geographical_location",
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]
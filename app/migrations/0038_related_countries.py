# Generated by Django 4.1.3 on 2022-11-14 17:05

import modelcluster.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0037_alter_articlepage_content_alter_projectpage_content_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="articlepage",
            name="related_countries",
            field=modelcluster.fields.ParentalManyToManyField(
                null=True, related_name="articles", to="app.countrypage"
            ),
        ),
        migrations.AddField(
            model_name="eventpage",
            name="related_countries",
            field=modelcluster.fields.ParentalManyToManyField(
                null=True, related_name="events", to="app.countrypage"
            ),
        ),
        migrations.AddField(
            model_name="opportunitypage",
            name="related_countries",
            field=modelcluster.fields.ParentalManyToManyField(
                null=True, related_name="opportunities", to="app.countrypage"
            ),
        ),
        migrations.AddField(
            model_name="organisationpage",
            name="related_countries",
            field=modelcluster.fields.ParentalManyToManyField(
                null=True, related_name="organisations", to="app.countrypage"
            ),
        ),
        migrations.AddField(
            model_name="personpage",
            name="related_countries",
            field=modelcluster.fields.ParentalManyToManyField(
                null=True, related_name="people", to="app.countrypage"
            ),
        ),
        migrations.AddField(
            model_name="projectpage",
            name="related_countries",
            field=modelcluster.fields.ParentalManyToManyField(
                null=True, related_name="projects", to="app.countrypage"
            ),
        ),
    ]
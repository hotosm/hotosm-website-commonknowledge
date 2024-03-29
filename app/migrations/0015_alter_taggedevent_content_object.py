# Generated by Django 4.1.1 on 2022-09-29 13:21

import django.db.models.deletion
import modelcluster.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0014_opportunitypage_opportunitytype_organisationpage_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="taggedevent",
            name="content_object",
            field=modelcluster.fields.ParentalKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="tagged_events",
                to="app.eventpage",
            ),
        ),
    ]

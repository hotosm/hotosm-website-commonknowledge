# Generated by Django 4.1.1 on 2022-11-02 05:09

import wagtail.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0023_alter_cmsimage_alt_text"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="articlepage",
            options={"ordering": ["-first_published_at"]},
        ),
        migrations.AlterModelOptions(
            name="countrypage",
            options={"ordering": ["title"]},
        ),
        migrations.AlterModelOptions(
            name="opportunitypage",
            options={"ordering": ["-first_published_at"]},
        ),
        migrations.AlterModelOptions(
            name="organisationpage",
            options={"ordering": ["title"]},
        ),
        migrations.AlterModelOptions(
            name="personpage",
            options={"ordering": ["title"]},
        ),
        migrations.AlterModelOptions(
            name="projectpage",
            options={"ordering": ["-first_published_at"]},
        ),
        migrations.AlterModelOptions(
            name="staticpage",
            options={"ordering": ["title"]},
        ),
        migrations.AlterField(
            model_name="activationindexpage",
            name="short_summary",
            field=wagtail.fields.RichTextField(blank=True, max_length=1500, null=True),
        ),
        migrations.AlterField(
            model_name="activationprojectpage",
            name="short_summary",
            field=wagtail.fields.RichTextField(blank=True, max_length=1500, null=True),
        ),
        migrations.AlterField(
            model_name="articlepage",
            name="short_summary",
            field=wagtail.fields.RichTextField(blank=True, max_length=1500, null=True),
        ),
        migrations.AlterField(
            model_name="countrypage",
            name="short_summary",
            field=wagtail.fields.RichTextField(blank=True, max_length=1500, null=True),
        ),
        migrations.AlterField(
            model_name="directorypage",
            name="short_summary",
            field=wagtail.fields.RichTextField(blank=True, max_length=1500, null=True),
        ),
        migrations.AlterField(
            model_name="eventpage",
            name="short_summary",
            field=wagtail.fields.RichTextField(blank=True, max_length=1500, null=True),
        ),
        migrations.AlterField(
            model_name="magazineindexpage",
            name="short_summary",
            field=wagtail.fields.RichTextField(blank=True, max_length=1500, null=True),
        ),
        migrations.AlterField(
            model_name="magazinesection",
            name="short_summary",
            field=wagtail.fields.RichTextField(blank=True, max_length=1500, null=True),
        ),
        migrations.AlterField(
            model_name="opportunitypage",
            name="short_summary",
            field=wagtail.fields.RichTextField(blank=True, max_length=1500, null=True),
        ),
        migrations.AlterField(
            model_name="organisationpage",
            name="short_summary",
            field=wagtail.fields.RichTextField(blank=True, max_length=1500, null=True),
        ),
        migrations.AlterField(
            model_name="personpage",
            name="short_summary",
            field=wagtail.fields.RichTextField(blank=True, max_length=1500, null=True),
        ),
        migrations.AlterField(
            model_name="projectpage",
            name="short_summary",
            field=wagtail.fields.RichTextField(blank=True, max_length=1500, null=True),
        ),
        migrations.AlterField(
            model_name="staticpage",
            name="short_summary",
            field=wagtail.fields.RichTextField(blank=True, max_length=1500, null=True),
        ),
        migrations.AlterField(
            model_name="topichomepage",
            name="short_summary",
            field=wagtail.fields.RichTextField(blank=True, max_length=1500, null=True),
        ),
        migrations.AlterField(
            model_name="topicpage",
            name="short_summary",
            field=wagtail.fields.RichTextField(blank=True, max_length=1500, null=True),
        ),
    ]

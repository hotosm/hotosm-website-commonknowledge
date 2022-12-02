# Generated by Django 4.1.3 on 2022-12-01 19:10

import django.db.models.deletion
import modelcluster.fields
import wagtail.blocks
import wagtail.fields
import wagtail.images.blocks
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0051_personpage_facebook_url_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="articlepage",
            name="added_authors",
            field=modelcluster.fields.ParentalManyToManyField(
                blank=True,
                help_text="Add authors who haven't manually edited the page through Wagtail",
                to="app.personpage",
            ),
        ),
        migrations.AddField(
            model_name="articlepage",
            name="authors",
            field=modelcluster.fields.ParentalManyToManyField(
                blank=True,
                help_text="Materialised list of authors",
                related_name="+",
                to="app.personpage",
            ),
        ),
        migrations.AddField(
            model_name="articlepage",
            name="hidden_authors",
            field=modelcluster.fields.ParentalManyToManyField(
                blank=True,
                help_text="authors who should be hidden from public citation",
                related_name="+",
                to="app.personpage",
            ),
        ),
        migrations.AddField(
            model_name="projectpage",
            name="related_people",
            field=modelcluster.fields.ParentalManyToManyField(
                blank=True, related_name="related_projects", to="app.personpage"
            ),
        ),
        migrations.AddField(
            model_name="topichomepage",
            name="added_authors",
            field=modelcluster.fields.ParentalManyToManyField(
                blank=True,
                help_text="Add authors who haven't manually edited the page through Wagtail",
                to="app.personpage",
            ),
        ),
        migrations.AddField(
            model_name="topichomepage",
            name="authors",
            field=modelcluster.fields.ParentalManyToManyField(
                blank=True,
                help_text="Materialised list of authors",
                related_name="+",
                to="app.personpage",
            ),
        ),
        migrations.AddField(
            model_name="topichomepage",
            name="hidden_authors",
            field=modelcluster.fields.ParentalManyToManyField(
                blank=True,
                help_text="authors who should be hidden from public citation",
                related_name="+",
                to="app.personpage",
            ),
        ),
        migrations.AddField(
            model_name="topicpage",
            name="added_authors",
            field=modelcluster.fields.ParentalManyToManyField(
                blank=True,
                help_text="Add authors who haven't manually edited the page through Wagtail",
                to="app.personpage",
            ),
        ),
        migrations.AddField(
            model_name="topicpage",
            name="authors",
            field=modelcluster.fields.ParentalManyToManyField(
                blank=True,
                help_text="Materialised list of authors",
                related_name="+",
                to="app.personpage",
            ),
        ),
        migrations.AddField(
            model_name="topicpage",
            name="hidden_authors",
            field=modelcluster.fields.ParentalManyToManyField(
                blank=True,
                help_text="authors who should be hidden from public citation",
                related_name="+",
                to="app.personpage",
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="is_public",
            field=models.BooleanField(
                blank=True,
                default=True,
                help_text="Setting this to false will hide the user's contributions from page author lists, and will not create a PersonPage either.",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="page",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="user",
                to="app.personpage",
            ),
        ),
    ]

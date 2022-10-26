# Generated by Django 4.1.1 on 2022-10-26 15:06

import django.db.models.deletion
import wagtail.blocks
import wagtail.fields
import wagtail.images.blocks
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("wagtailcore", "0077_alter_revision_user"),
        ("app", "0020_activationindexpage_frontmatter_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="CountryPage",
            fields=[
                (
                    "page_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="wagtailcore.page",
                    ),
                ),
                (
                    "image_url",
                    models.URLField(
                        blank=True,
                        help_text="If set, this image will be used instead of the featured image.",
                        null=True,
                    ),
                ),
                (
                    "short_summary",
                    models.CharField(blank=True, max_length=1500, null=True),
                ),
                (
                    "frontmatter",
                    models.JSONField(
                        blank=True, help_text="Metadata from the legacy site", null=True
                    ),
                ),
                (
                    "content",
                    wagtail.fields.StreamField(
                        [
                            ("richtext", wagtail.blocks.RichTextBlock()),
                            (
                                "embeddable_code",
                                wagtail.blocks.StructBlock(
                                    [
                                        (
                                            "description",
                                            wagtail.blocks.RichTextBlock(
                                                help_text="(Internal use only.) Explain what this does for other editors. Not displayed on the website.",
                                                required=False,
                                            ),
                                        ),
                                        (
                                            "html",
                                            wagtail.blocks.CharBlock(max_length=10000),
                                        ),
                                    ]
                                ),
                            ),
                            (
                                "links_gallery",
                                wagtail.blocks.StructBlock(
                                    [
                                        (
                                            "title",
                                            wagtail.blocks.CharBlock(max_length=250),
                                        ),
                                        (
                                            "description",
                                            wagtail.blocks.RichTextBlock(
                                                required=False
                                            ),
                                        ),
                                        (
                                            "links",
                                            wagtail.blocks.ListBlock(
                                                wagtail.blocks.StructBlock(
                                                    [
                                                        (
                                                            "page",
                                                            wagtail.blocks.PageChooserBlock(
                                                                required=False
                                                            ),
                                                        ),
                                                        (
                                                            "label",
                                                            wagtail.blocks.CharBlock(
                                                                help_text="Will override the page title if specified",
                                                                max_length=250,
                                                                required=False,
                                                            ),
                                                        ),
                                                        (
                                                            "url",
                                                            wagtail.blocks.URLBlock(
                                                                help_text="Will override the page URL if specified",
                                                                max_length=1000,
                                                                required=False,
                                                            ),
                                                        ),
                                                        (
                                                            "description",
                                                            wagtail.blocks.CharBlock(
                                                                max_length=250,
                                                                required=False,
                                                            ),
                                                        ),
                                                    ]
                                                )
                                            ),
                                        ),
                                        (
                                            "more_info",
                                            wagtail.blocks.StructBlock(
                                                [
                                                    (
                                                        "page",
                                                        wagtail.blocks.PageChooserBlock(
                                                            required=False
                                                        ),
                                                    ),
                                                    (
                                                        "label",
                                                        wagtail.blocks.CharBlock(
                                                            help_text="Will override the page title if specified",
                                                            max_length=250,
                                                            required=False,
                                                        ),
                                                    ),
                                                    (
                                                        "url",
                                                        wagtail.blocks.URLBlock(
                                                            help_text="Will override the page URL if specified",
                                                            max_length=1000,
                                                            required=False,
                                                        ),
                                                    ),
                                                    (
                                                        "description",
                                                        wagtail.blocks.CharBlock(
                                                            max_length=250,
                                                            required=False,
                                                        ),
                                                    ),
                                                ],
                                                required=False,
                                            ),
                                        ),
                                    ]
                                ),
                            ),
                            (
                                "featured_link",
                                wagtail.blocks.StructBlock(
                                    [
                                        (
                                            "title",
                                            wagtail.blocks.CharBlock(
                                                help_text="Will override the page title if specified",
                                                max_length=250,
                                            ),
                                        ),
                                        ("description", wagtail.blocks.RichTextBlock()),
                                        (
                                            "image",
                                            wagtail.images.blocks.ImageChooserBlock(
                                                required=False
                                            ),
                                        ),
                                        (
                                            "link_page",
                                            wagtail.blocks.PageChooserBlock(
                                                required=False
                                            ),
                                        ),
                                        (
                                            "link_label",
                                            wagtail.blocks.CharBlock(
                                                help_text="Will override the page title if specified",
                                                max_length=250,
                                                required=False,
                                            ),
                                        ),
                                        (
                                            "link_url",
                                            wagtail.blocks.URLBlock(
                                                help_text="Will override the page URL if specified",
                                                max_length=1000,
                                                required=False,
                                            ),
                                        ),
                                    ]
                                ),
                            ),
                            (
                                "simple_link",
                                wagtail.blocks.StructBlock(
                                    [
                                        (
                                            "page",
                                            wagtail.blocks.PageChooserBlock(
                                                required=False
                                            ),
                                        ),
                                        (
                                            "label",
                                            wagtail.blocks.CharBlock(
                                                help_text="Will override the page title if specified",
                                                max_length=250,
                                                required=False,
                                            ),
                                        ),
                                        (
                                            "url",
                                            wagtail.blocks.URLBlock(
                                                help_text="Will override the page URL if specified",
                                                max_length=1000,
                                                required=False,
                                            ),
                                        ),
                                        (
                                            "description",
                                            wagtail.blocks.CharBlock(
                                                max_length=250, required=False
                                            ),
                                        ),
                                    ]
                                ),
                            ),
                        ],
                        blank=True,
                        null=True,
                        use_json_field=True,
                    ),
                ),
                ("isoa2", models.CharField(max_length=2, unique=True)),
                ("isoa3", models.CharField(max_length=3, unique=True)),
                ("continent", models.CharField(blank=True, max_length=50, null=True)),
                (
                    "featured_image",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="app.cmsimage",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=("wagtailcore.page",),
        ),
    ]

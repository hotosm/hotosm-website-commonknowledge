from email.policy import default

from django.db import models
from wagtail import blocks
from wagtail.admin.panels import FieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.fields import RichTextField, StreamField

from app.models.wagtail.blocks import (
    ExternalLinkBlock,
    InternalLinkBlock,
    LinkStreamBlock,
)


@register_setting(icon="list-ul")
class HeaderSetting(BaseSiteSetting):
    class Meta:
        verbose_name = "Header"

    navigation = StreamField(
        [
            ("internal_link", InternalLinkBlock()),
            ("external_link", ExternalLinkBlock()),
        ],
        max_num=5,
        null=True,
        blank=True,
        use_json_field=True,
    )

    button = StreamField(
        [
            ("internal_link", InternalLinkBlock()),
            ("external_link", ExternalLinkBlock()),
        ],
        max_num=1,
        null=True,
        blank=True,
        use_json_field=True,
    )

    panels = [
        FieldPanel("navigation"),
        FieldPanel("button"),
    ]


class SectionBlock(blocks.StructBlock):
    title = blocks.CharBlock()
    links = LinkStreamBlock(min_num=1, max_num=10)


@register_setting(icon="list-ul")
class FooterSetting(BaseSiteSetting):
    class Meta:
        verbose_name = "Footer"

    description = models.CharField(
        blank=True,
        null=True,
        max_length=200,
        default="Humanitarian OpenStreetMap Team (HOT) sits at the nexus of participatory mapping, community-led development, humanitarian response, open data and tech.",
    )
    navigation = StreamField(
        [("nav_section", SectionBlock())],
        max_num=4,
        null=True,
        blank=True,
        use_json_field=True,
    )

    panels = [
        FieldPanel("description"),
        FieldPanel("navigation"),
    ]

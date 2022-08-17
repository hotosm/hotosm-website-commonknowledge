from django.db import models
from wagtail import blocks
from wagtail.admin.panels import FieldPanel, ObjectList, TabbedInterface
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page

import app.models.wagtail.blocks as app_blocks

block_features = [
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "bold",
    "italic",
    "link",
    "ol",
    "ul",
    "hr",
    "link",
    "document-link",
    "image",
    "embed",
    "blockquote",
]


class HomePage(Page):
    parent_page_type = []
    show_in_menus_default = True
    layout = StreamField(
        [
            ("summary_text", app_blocks.PageSummaryBlock()),
            ("richtext", blocks.RichTextBlock()),
        ],
        null=True,
        blank=True,
        use_json_field=True,
    )
    content_panels = Page.content_panels + [FieldPanel("layout")]


class StaticPage(Page):
    show_in_menus_default = True

    # Content
    layout = StreamField(
        [
            ("richtext", blocks.RichTextBlock()),
            ("embeddable_code", app_blocks.HTMLBlock()),
        ],
        null=True,
        blank=True,
        use_json_field=True,
    )
    content_panels = Page.content_panels + [FieldPanel("layout")]

    # Layout
    show_header = models.BooleanField(default=True)
    show_footer = models.BooleanField(default=True)
    layout_panels = [FieldPanel("show_header"), FieldPanel("show_footer")]

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(layout_panels, heading="Layout"),
            ObjectList(Page.promote_panels, heading="Promote"),
            ObjectList(Page.settings_panels, heading="Settings", classname="settings"),
        ]
    )


class MagazineIndexPage(Page):
    max_count_per_parent = 1
    parent_page_type = ["app.HomePage"]
    subpage_types = [
        "app.MagazineArticlePage",
    ]
    show_in_menus_default = True
    # layout = StreamField([

    # ], null=True, blank=True, use_json_field=True)
    # content_panels = Page.content_panels + [FieldPanel("layout")]


class MagazineArticlePage(Page):
    parent_page_type = ["app.MagazineIndexPage"]
    show_in_menus_default = True
    article = RichTextField()
    layout = StreamField(
        [
            ("richtext", blocks.RichTextBlock()),
            ("embeddable_code", app_blocks.HTMLBlock()),
        ],
        null=True,
        blank=True,
        use_json_field=True,
    )
    content_panels = Page.content_panels + [FieldPanel("layout")]
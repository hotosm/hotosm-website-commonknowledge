from wagtail import blocks
from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField
from wagtail.models import Page

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
            ("richtext", blocks.RichTextBlock()),
        ],
        null=True,
        blank=True,
        use_json_field=True,
    )
    content_panels = Page.content_panels + [FieldPanel("layout")]


class StaticPage(Page):
    show_in_menus_default = True
    layout = StreamField(
        [
            ("richtext", blocks.RichTextBlock()),
        ],
        null=True,
        blank=True,
        use_json_field=True,
    )
    content_panels = Page.content_panels + [FieldPanel("layout")]


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
    layout = StreamField(
        [
            ("richtext", blocks.RichTextBlock()),
        ],
        null=True,
        blank=True,
        use_json_field=True,
    )
    content_panels = Page.content_panels + [FieldPanel("layout")]

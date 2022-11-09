from django.utils.translation import gettext_lazy as _
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock

from app.utils.github import github_repo_validator
from app.utils.hotosm import task_manager_project_url_validator


class PageSummaryBlock(blocks.StructBlock):
    text = blocks.RichTextBlock(form_classname="full")

    class Meta:
        template = "app/blocks/page_summary_block.html"


class HTMLBlock(blocks.StructBlock):
    description = blocks.RichTextBlock(
        help_text="(Internal use only.) Explain what this does for other editors. Not displayed on the website.",
        required=False,
    )
    html = blocks.CharBlock(max_length=10000)

    class Meta:
        template = "app/blocks/html_block.html"


class LinkBlock(blocks.StructBlock):
    page = blocks.PageChooserBlock(required=False)
    label = blocks.CharBlock(
        required=False,
        max_length=250,
        help_text="Will override the page title if specified",
    )
    url = blocks.URLBlock(
        required=False,
        max_length=1000,
        help_text="Will override the page URL if specified",
    )
    description = blocks.CharBlock(max_length=250, required=False)

    class Meta:
        template = "app/blocks/link_block.html"


class FeaturedLinkBlock(blocks.StructBlock):
    title = blocks.CharBlock(
        max_length=250, help_text="Will override the page title if specified"
    )
    description = blocks.RichTextBlock()
    image = ImageChooserBlock(required=False)

    link_page = blocks.PageChooserBlock(required=False)
    link_label = blocks.CharBlock(
        required=False,
        max_length=250,
        help_text="Will override the page title if specified",
    )
    link_url = blocks.URLBlock(
        required=False,
        max_length=1000,
        help_text="Will override the page URL if specified",
    )

    class Meta:
        template = "app/blocks/featured_link_block.html"


class GuideSection(blocks.StructBlock):
    title = blocks.CharBlock(max_length=250)
    description = blocks.RichTextBlock(required=False)
    links = blocks.ListBlock(LinkBlock())
    more_info = LinkBlock(required=False)

    class Meta:
        template = "app/blocks/guide_section_block.html"


class HomepageSectionBlock(blocks.StructBlock):
    title = blocks.CharBlock(max_length=150)
    subtitle = blocks.CharBlock(max_length=250, required=False)
    links = blocks.ListBlock(LinkBlock())

    class Meta:
        template = "app/blocks/homepage_section_block.html"


class HomepageMapBlock(blocks.StructBlock):
    class Meta:
        template = "app/blocks/homepage_map_block.html"


class HomepageMagazineBlock(blocks.StructBlock):
    class Meta:
        template = "app/blocks/homepage_magazine_block.html"


class MetricsBlock(blocks.StructBlock):
    class Meta:
        template = "app/blocks/metric_block.html"
        icon = "fa fa-list-ol"

    metrics = blocks.ListBlock(
        blocks.StructBlock(
            [
                (
                    "value",
                    blocks.CharBlock(
                        required=True,
                        help_text="The metric to display, usually a number. For example: 45",
                    ),
                ),
                (
                    "label",
                    blocks.CharBlock(
                        required=True,
                        help_text="The name of the metric. For example: areas mapped",
                    ),
                ),
            ]
        ),
        max_num=4,
        min_number=1,
    )


class ImageBlock(blocks.StructBlock):
    class Meta:
        # TODO:
        template = "app/blocks/dummy_block.html"
        icon = "fa fa-picture-o"

    image = ImageChooserBlock(required=True)
    caption = blocks.CharBlock(required=False)


class LinkStreamBlock(blocks.StreamBlock):
    internal_link = blocks.StructBlock(
        [
            ("page", blocks.PageChooserBlock(required=True)),
            (
                "label",
                blocks.CharBlock(
                    required=False, help_text="If set this replaces the page title"
                ),
            ),
        ]
    )
    external_link = blocks.StructBlock(
        [
            ("url", blocks.URLBlock(required=True)),
            ("label", blocks.CharBlock(required=True)),
        ]
    )


class TaskManagerProjectBlock(blocks.StructBlock):
    class Meta:
        template = "app/blocks/dummy_block.html"
        icon = "fa fa-map-o"

    url = blocks.URLBlock(
        validators=[task_manager_project_url_validator], required=True
    )


class FeaturedContentBlock(blocks.StructBlock):
    """
    This is a big fancy block meant for embeddable stuff...
    """

    class Meta:
        # TODO:
        template = "app/blocks/dummy_block.html"
        icon = "fa fa-map-signs"

    title = blocks.CharBlock(required=True, max_length=100)
    description = blocks.RichTextBlock(
        required=False, max_length=500, features=["italic", "bold", "link"]
    )
    links = LinkStreamBlock(min_num=1, max_num=3)
    featured_content = blocks.StreamBlock(
        [
            ("single_image", ImageChooserBlock()),
            (
                "multiple_images",
                blocks.ListBlock(ImageChooserBlock(), icon="fa fa-picture-o"),
            ),
            ("single_task_manager_project", TaskManagerProjectBlock()),
            (
                "multiple_task_manager_projects",
                blocks.ListBlock(TaskManagerProjectBlock(), icon="fa fa-map-o"),
            ),
            (
                "github_repo",
                blocks.URLBlock(
                    validators=[github_repo_validator], icon="fa fa-github"
                ),
            ),
        ],
        min_num=1,
        max_num=1,
    )


class CallToActionBlock(blocks.StructBlock):
    """
    This is a more boring but versatile block for adding links to things, optionally with an image
    """

    class Meta:
        # TODO:
        template = "app/blocks/dummy_block.html"
        icon = "fa fa-map-signs"

    title = blocks.CharBlock(max_length=75, required=True)
    description = blocks.RichTextBlock(
        required=False, max_length=200, features=["italic", "bold", "link"]
    )
    links = LinkStreamBlock(min_num=1, max_num=2)
    image = ImageChooserBlock(required=False)
    size = blocks.ChoiceBlock(
        choices=[
            ("lg", "Large"),
            ("md", "Medium"),
            ("sm", "Small"),
        ],
        default="sm",
    )


class PageLinkBlock(blocks.StructBlock):
    """
    This is the simplest block
    """

    class Meta:
        # TODO:
        template = "app/blocks/dummy_block.html"
        icon = "fa fa-link"

    page = blocks.PageChooserBlock(required=True)
    include_page_actions = blocks.BooleanBlock(
        default=True,
        help_text="Find and display any quick links set up inside the Page, like 'Download Tool' or 'Read Guide'",
    )
    size = blocks.ChoiceBlock(
        choices=[
            ("lg", "Large (more previewed content)"),
            ("md", "Medium"),
            ("sm", "Small (least previewed content)"),
        ],
        default="sm",
    )


class GalleryBlock(blocks.StructBlock):
    class Meta:
        # TODO:
        template = "app/blocks/dummy_block.html"
        icon = "fa fa-th-large"

    title = blocks.CharBlock(max_length=100, required=False)
    subtitle = blocks.CharBlock(max_length=100, required=False)


class PageLinkGalleryBlock(GalleryBlock):
    pages = blocks.ListBlock(PageLinkBlock())


class CallToActionGalleryBlock(GalleryBlock):
    pages = blocks.ListBlock(CallToActionBlock())


class RelatedPeopleBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=False)
    description = blocks.RichTextBlock(
        features=["italic", "bold", "link"], required=False
    )

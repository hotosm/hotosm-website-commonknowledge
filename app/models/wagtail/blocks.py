from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock


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

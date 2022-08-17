from wagtail import blocks


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

from wagtail import blocks


class PageSummaryBlock(blocks.StructBlock):
    text = blocks.RichTextBlock(form_classname="full")

    class Meta:
        template = "app/blocks/page_summary_block.html"

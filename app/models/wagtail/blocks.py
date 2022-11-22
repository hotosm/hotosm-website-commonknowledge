from django.utils.translation import gettext_lazy as _
from wagtail import blocks
from wagtail.core.blocks import StructValue
from wagtail.images.blocks import ImageChooserBlock

from app.utils.github import github_repo_validator
from app.utils.hotosm import task_manager_project_url_validator
from app.utils.wagtail import localized_pages


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
        help_text = "Block that displays numbers with a description under them."

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
        min_num=1,
    )


class ImageBlock(blocks.StructBlock):
    class Meta:
        # TODO:
        template = "app/blocks/dummy_block.html"
        icon = "fa fa-picture-o"

    image = ImageChooserBlock(required=True)
    caption = blocks.CharBlock(required=False)


class InternalLinkValue(StructValue):
    def url(self):
        return self.get("page").localized.url

    def text(self):
        if len(self.get("label")):
            return self.get("label")
        return self.get("page").localized.title


class InternalLinkBlock(blocks.StructBlock):
    page = blocks.PageChooserBlock(required=True)
    label = blocks.CharBlock(
        required=False, help_text="If set this replaces the page title"
    )

    class Meta:
        value_class = InternalLinkValue


class ExternalLinkValue(StructValue):
    def text(self):
        return self.get("label")


class ExternalLinkBlock(blocks.StructBlock):
    url = blocks.URLBlock(required=True)
    label = blocks.CharBlock(required=True)

    class Meta:
        value_class = ExternalLinkValue


class LinkStreamBlock(blocks.StreamBlock):
    internal_link = InternalLinkBlock()
    external_link = ExternalLinkBlock()

    def link(self, *args, **kwargs):
        print("Called", args, kwargs)
        return None


class TaskManagerProjectBlock(blocks.StructBlock):
    class Meta:
        template = "app/blocks/dummy_block.html"
        icon = "fa fa-map-o"

    url = blocks.URLBlock(
        validators=[task_manager_project_url_validator], required=True
    )


# class FeaturedContentBlock(blocks.StructBlock):
#     """
#     This is a big fancy block meant for embeddable stuff...
#     """

#     class Meta:
#         # TODO:
#         template = "app/blocks/dummy_block.html"
#         icon = "fa fa-map-signs"

#     title = blocks.CharBlock(required=True, max_length=100)
#     description = blocks.RichTextBlock(
#         required=False, max_length=500, features=["italic", "bold", "link"]
#     )
#     links = LinkStreamBlock(min_num=1, max_num=3)
#     featured_content = blocks.StreamBlock(
#         [
#             ("single_image", ImageChooserBlock()),
#             (
#                 "multiple_images",
#                 blocks.ListBlock(ImageChooserBlock(), icon="fa fa-picture-o"),
#             ),
#             ("single_task_manager_project", TaskManagerProjectBlock()),
#             (
#                 "multiple_task_manager_projects",
#                 blocks.ListBlock(TaskManagerProjectBlock(),
#                                  icon="fa fa-map-o"),
#             ),
#             (
#                 "github_repo",
#                 blocks.URLBlock(
#                     validators=[github_repo_validator], icon="fa fa-github"
#                 ),
#             ),
#         ],
#         min_num=1,
#         max_num=1,
#     )


class SimpleCallToActionBlock(blocks.StructBlock):
    """
    This is a more boring but versatile block for adding links to things, optionally with an image
    """

    class Meta:
        template = "app/blocks/call_to_action_block.html"
        icon = "fa fa-map-signs"

    title = blocks.CharBlock(max_length=75, required=True)
    description = blocks.RichTextBlock(
        required=False, max_length=400, features=["italic", "bold", "link"]
    )
    image = ImageChooserBlock(required=False)
    links = LinkStreamBlock(min_num=0, max_num=2, required=False)


class LargeCallToActionBlock(SimpleCallToActionBlock):
    """
    This is a more boring but versatile block for adding links to things, optionally with an image
    """

    class Meta:
        template = "app/blocks/call_to_action_block.html"
        icon = "fa fa-map-signs"

    background = blocks.ChoiceBlock(
        choices=[
            ("dark", "Dark"),
            ("light", "Light"),
        ],
        default="light",
    )

    layout = blocks.ChoiceBlock(
        choices=[
            ("image_left", "Image left"),
            ("image_right", "Image right"),
        ],
        default="image_left",
    )


class CallToActionGalleryBlock(blocks.StructBlock):
    class Meta:
        template = "app/blocks/call_to_action_gallery_block.html"
        icon = "fa fa-th-large"

    rows = blocks.ListBlock(
        blocks.ListBlock(SimpleCallToActionBlock(), min_num=1, max_num=3),
        help_text="A lone item in a row will be displayed full width. More items per row means visually smaller items.",
    )


class RelatedPeopleBlock(blocks.StructBlock):
    class Meta:
        # TODO:
        template = "app/blocks/dummy_block.html"
        icon = "fa fa-users"

    title = blocks.CharBlock(required=False)
    description = blocks.RichTextBlock(
        features=["italic", "bold", "link"], required=False
    )


class CarouselBlock(blocks.StructBlock):
    class Meta:
        template = "app/blocks/carousel_block.html"

    title = blocks.CharBlock(required=True)


class LatestArticles(CarouselBlock):
    class Meta:
        template = "app/blocks/latest_articles.html"

    def get_context(self, value, parent_context=None):
        from app.models.wagtail import ArticlePage, MagazineIndexPage

        context = super().get_context(value, parent_context=parent_context)
        articles = localized_pages(
            ArticlePage.objects.all()
            .live()
            .public()
            .order_by("-first_published_at")[:6]
        )

        context["view_all"] = MagazineIndexPage.objects.live().public().first()
        context["pages"] = articles
        return context


class FeaturedProjects(CarouselBlock):
    class Meta:
        template = "app/blocks/featured_projects.html"

    ProjectsChooser = blocks.ListBlock(
        blocks.PageChooserBlock(page_type="app.ProjectPage")
    )

    def get_context(self, value, parent_context=None):

        context = super().get_context(value, parent_context=parent_context)
        context["pages"] = value["ProjectsChooser"]
        return context


class HeadingAndSubHeadingBlock(blocks.StructBlock):
    class Meta:
        template = "app/blocks/heading_and_subheading.html"

    title = blocks.CharBlock(max_length=75, required=True)
    description = blocks.RichTextBlock(
        required=True,
        max_length=400,
        features=["italic", "bold", "link"],
    )


class PartnerLogos(blocks.StructBlock):
    class Meta:
        template = "app/blocks/partner_logos.html"
        help_text = "Display a list of partner organisations' logos and links."

    title = blocks.CharBlock(required=True)

    partners = blocks.ListBlock(
        blocks.StructBlock(
            [
                ("logo", ImageChooserBlock(required=True)),
                ("url", blocks.URLBlock(required=True)),
            ]
        )
    )


class ImpactAreaCarousel(blocks.StructBlock):
    class Meta:
        template = "app/blocks/impact_area_carousel.html"
        help_text = "Interactive carousel of all impact areas. Clicking to navigate to the page."

    def get_context(self, value, parent_context=None):
        from app.models.wagtail import ImpactAreaPage

        context = super().get_context(value, parent_context=parent_context)
        impact_areas = localized_pages(ImpactAreaPage.objects.all().live().public())
        context["impact_areas"] = impact_areas
        return context

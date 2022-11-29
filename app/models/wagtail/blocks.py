from math import floor

from django.conf import settings
from django.utils.translation import gettext_lazy as _
from wagtail import blocks
from wagtail.core.blocks import StructValue
from wagtail.images.blocks import ImageChooserBlock

from app.utils.github import github_repo_validator
from app.utils.hotosm import task_manager_project_url_validator
from app.utils.wagtail import localized_pages


class HTMLBlock(blocks.StructBlock):
    description = blocks.RichTextBlock(
        help_text="(Internal use only.) Explain what this does for other editors. Not displayed on the website.",
        required=False,
    )
    html = blocks.CharBlock(max_length=10000)

    class Meta:
        template = "app/blocks/html_block.html"
        group = "Special"


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
        group = "Special"

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
        template = "app/blocks/image_block.html"
        icon = "fa fa-picture-o"
        group = "Basic"

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


class TitleTextImageBlock(blocks.StructBlock):
    class Meta:
        template = "app/blocks/title_text_image_block.html"
        help_text = "A title, a block of text, two links and a image on the left or right hand side"
        group = "Section headings"

    title = blocks.CharBlock(required=True, help_text="The title of the block")
    description = blocks.CharBlock(
        required=True, help_text="A description displayed under the title"
    )
    image = ImageChooserBlock(
        required=True,
        help_text="An image, displayed on the left or right of the title and description",
    )
    links = blocks.ListBlock(LinkBlock())

    layout = blocks.ChoiceBlock(
        choices=[
            ("image_right", "Image right"),
            ("image_left", "Image left"),
        ],
        default="image_left",
    )


class TaskManagerProjectBlock(blocks.StructBlock):
    class Meta:
        template = "app/blocks/dummy_block.html"
        icon = "fa fa-map-o"

    url = blocks.URLBlock(
        validators=[task_manager_project_url_validator], required=True
    )


class SimpleCallToActionBlock(blocks.StructBlock):
    """
    This is a more boring but versatile block for adding links to things, optionally with an image
    """

    class Meta:
        template = "app/blocks/call_to_action_block.html"
        icon = "fa fa-map-signs"
        group = "Links"

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
        group = "Links"

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
        group = "Links"

    rows = blocks.ListBlock(
        blocks.ListBlock(SimpleCallToActionBlock(), min_num=1, max_num=3),
        help_text="A lone item in a row will be displayed full width. More items per row means visually smaller items.",
    )


class CarouselBlock(blocks.StructBlock):
    class Meta:
        template = "app/blocks/carousel_block.html"
        group = "Related content"

    title = blocks.CharBlock(required=True)


class LatestArticles(CarouselBlock):
    class Meta:
        template = "app/blocks/latest_articles.html"
        group = "Related content"

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


class LatestOpportunities(CarouselBlock):
    class Meta:
        template = "app/blocks/latest_opportunities.html"
        group = "Related content"
        help_text = "A horizontal list of opportunities avaliable for volunteering and otherwise helping out HOT."

    opportunities_shown = blocks.ChoiceBlock(
        choices=[
            ("show_all", "Show all opportunities across the site"),
            ("only_children", "Only show opportunities that are childen of this page"),
        ],
        default="show_all",
        help_text="This block can show all opportunites across the HOT site, or only those opportunities that are under this page.",
    )

    def get_context(self, value, parent_context=None):
        from app.models.wagtail import MagazineIndexPage, OpportunityPage

        context = super().get_context(value, parent_context=parent_context)

        if value["opportunities_shown"] == "show_all":
            opportunities = localized_pages(
                OpportunityPage.objects.all()
                .live()
                .public()
                .order_by("-first_published_at")[:6]
            )
        else:
            opportunities = localized_pages(
                OpportunityPage.objects.all()
                .live()
                .child_of(context["page"])
                .public()
                .order_by("-first_published_at")[:6]
            )

        context["pages"] = opportunities

        return context


class FeaturedProjects(CarouselBlock):
    class Meta:
        template = "app/blocks/featured_projects.html"
        group = "Related content"

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
        group = "Section headings"

    title = blocks.CharBlock(max_length=75, required=True)
    description = blocks.RichTextBlock(
        required=True,
        max_length=600,
        features=["italic", "bold", "link"],
    )


class ResourcesBlock(blocks.StructBlock):
    class Meta:
        template = "app/blocks/resources_block.html"
        group = "Related content"
        help_text = "Display a set of resources, including popular resources."

    first_highlighted_resource = blocks.PageChooserBlock()
    second_highlighted_resource = blocks.PageChooserBlock()
    popular_resources = blocks.ListBlock(
        LinkBlock(), min=1, help_text="Popular resources to highlight"
    )
    view_all_link = LinkBlock()


class TeamCarouselBlock(blocks.StructBlock):
    class Meta:
        template = "app/blocks/team_carousel_block.html"
        group = "Related content"
        help_text = "A carousel of team members."

    title = blocks.CharBlock(max_length=75, required=True)
    description = blocks.RichTextBlock(
        required=True,
        max_length=400,
        features=[],
    )
    team = blocks.ListBlock(blocks.PageChooserBlock(page_type="app.PersonPage"))


class PartnerLogos(blocks.StructBlock):
    class Meta:
        template = "app/blocks/partner_logos.html"
        help_text = "Display a list of partner organisations' logos and links."
        group = "Special"

    title = blocks.CharBlock(required=True)

    partners = blocks.ListBlock(
        blocks.StructBlock(
            [
                ("logo", ImageChooserBlock(required=True)),
                ("url", blocks.URLBlock(required=True)),
            ]
        )
    )


class MapBlock(blocks.StructBlock):
    class Meta:
        template = "app/blocks/map_block.html"
        help_text = "Explorable map with pin-pointed links to the rest of the site."
        group = "Special"

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context)
        context["MAPBOX_PUBLIC_API_KEY"] = settings.MAPBOX_PUBLIC_API_KEY
        return context


class ImpactAreaCarousel(blocks.StructBlock):
    class Meta:
        template = "app/blocks/impact_area_carousel.html"
        help_text = "Interactive carousel of all impact areas. Clicking to navigate to the page."
        group = "Related content"

    def get_context(self, value, parent_context=None):
        from app.models.wagtail import ImpactAreaPage

        context = super().get_context(value, parent_context=parent_context)
        impact_areas = localized_pages(ImpactAreaPage.objects.all().live().public())
        context["impact_areas"] = impact_areas
        context["starting_index"] = max(0, floor(len(impact_areas) / 2) - 1)
        return context


class TestimonialsSliderBlock(blocks.StructBlock):
    class Meta:
        group = "Basic"
        help_text = "A set of testimonials, inside a carousel."
        template = "app/blocks/testimonials_slider_block.html"

    testimonials = blocks.ListBlock(
        blocks.StructBlock(
            [
                (
                    "quote",
                    blocks.RichTextBlock(
                        required=True,
                        max_length=400,
                        features=[],
                    ),
                ),
                ("image", ImageChooserBlock(required=True)),
                ("name", blocks.CharBlock(required=True)),
                ("location", blocks.CharBlock(required=False)),
            ]
        )
    )


full_width_blocks = [
    ("richtext", blocks.RichTextBlock(group="Basic")),
    ("image", ImageBlock()),
    ("call_to_action", LargeCallToActionBlock()),
    ("gallery_of_calls_to_action", CallToActionGalleryBlock()),
    ("metrics", MetricsBlock()),
    ("team_carousel", TeamCarouselBlock()),
    ("html", HTMLBlock()),
    ("heading_and_subheading", HeadingAndSubHeadingBlock()),
    ("partner_logos", PartnerLogos()),
    ("title_text_image", TitleTextImageBlock()),
    ("impact_area_carousel", ImpactAreaCarousel()),
    ("latest_articles", LatestArticles()),
    ("featured_projects", FeaturedProjects()),
    ("latest_opportunities", LatestOpportunities()),
    ("map", MapBlock()),
    ("testimonials_slider_block", TestimonialsSliderBlock()),
    ("resources", ResourcesBlock()),
]

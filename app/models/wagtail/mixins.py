import json

from django.contrib.gis.db.models import PointField
from django.contrib.postgres.search import SearchHeadline, SearchQuery
from django.core.paginator import Paginator
from django.db import models
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from mapwidgets.widgets import MapboxPointFieldWidget
from modelcluster.fields import ParentalManyToManyField
from wagtail import blocks
from wagtail.admin.panels import (
    FieldPanel,
    FieldRowPanel,
    MultiFieldPanel,
    ObjectList,
    TabbedInterface,
)
from wagtail.api.conf import APIField
from wagtail.core.models import Page
from wagtail.fields import RichTextField, StreamField
from wagtail.search.models import Query
from wagtail_localize.fields import SynchronizedField
from wagtailautocomplete.edit_handlers import AutocompletePanel

import app.models.wagtail.blocks as app_blocks
from app.helpers import concat_html, safe_to_int
from app.utils.geo import geolocator
from app.utils.python import ensure_1D_list
from app.utils.wagtail import localized_related_pages

from .cms import CMSImage


class PreviewablePage(Page):
    class Meta:
        abstract = True

    template = "app/static_page.html"

    # Fields
    featured_image = models.ForeignKey(
        CMSImage,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    short_summary = RichTextField(max_length=1500, blank=True, null=True)
    frontmatter = models.JSONField(
        blank=True, null=True, help_text="Metadata from the legacy site"
    )

    # Make the slug synchronised, but don't allow it to be overridden on translations
    override_translatable_fields = [
        SynchronizedField("featured_image", overridable=False),
        SynchronizedField("frontmatter", overridable=False),
    ]

    list_card_template = "app/cards/generic_list_card.html"

    @property
    def resolved_theme_class(self):
        if (
            hasattr(self, "theme_class")
            and self.theme_class is not None
            and len(self.theme_class) > 0
        ):
            return self.theme_class
        for nearest_ancestor in reversed(self.get_ancestors()):
            nearest_ancestor = nearest_ancestor.specific
            if (
                hasattr(nearest_ancestor, "theme_class")
                and nearest_ancestor.theme_class is not None
                and len(nearest_ancestor.theme_class) > 0
            ):
                return nearest_ancestor.theme_class
        return "theme-blue"

    @property
    def label(self):
        """
        What kind of page is this? For use in templates.
        """

        return self._meta.verbose_name.removesuffix(" page")

    @property
    def date(self):
        """
        Article date for use in templates
        """

        if self.first_published_at is not None:
            return self.first_published_at
        return self.last_published_at

    def autocomplete_label(self):
        return f"[{self.locale.language_code.upper()}] {self.title}"

    filter_url_key = "translation_key"

    @property
    def filter_url_value(self):
        return getattr(self, self.filter_url_key)

    @property
    def summary(self):
        """
        Summary text for use in templates: the short_summary if this has been set or the first Richtext we find in the content
        """
        if self.short_summary is not None and len(self.short_summary) > 0:
            return self.short_summary
        if hasattr(self, "content") and self.content is not None:
            try:
                for block in self.content:
                    if block.block_type == "richtext":
                        return block.value
            except:
                return None

    # Methods
    @property
    def image(self):
        """
        Image for use in templates, such as cards. Will use `featured_image` or else the first image found in the content.
        """
        if self.featured_image is not None:
            return self.featured_image
        if hasattr(self, "content") and self.content is not None:
            try:
                for block in self.content:
                    if block.block_type == "image":
                        return block.value
            except:
                return None

    # Editor
    previewable_page_panels = [
        FieldPanel("short_summary"),
        FieldPanel("featured_image"),
    ]
    content_panels = Page.content_panels + previewable_page_panels

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(Page.promote_panels, heading="Sharing"),
            ObjectList(
                Page.settings_panels,
                heading="Publishing Schedule",
                classname="settings",
            ),
        ]
    )


class ContentPage(PreviewablePage):
    class Meta:
        abstract = True

    # Fields
    content = StreamField(
        app_blocks.full_width_blocks,
        null=True,
        blank=True,
        use_json_field=True,
    )

    # Editor
    content_page_panels = [
        FieldPanel("content"),
    ]
    content_panels = PreviewablePage.content_panels + content_page_panels

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(Page.promote_panels, heading="Sharing"),
            ObjectList(
                Page.settings_panels,
                heading="Publishing Schedule",
                classname="settings",
            ),
        ]
    )


class ContentSidebarPage(PreviewablePage):
    class Meta:
        abstract = True

    # This is for the narrow center-column
    # So full-width blocks are not appropriate here
    content = StreamField(
        [
            ("richtext", blocks.RichTextBlock(group="Basic")),
            ("image", app_blocks.ImageBlock()),
            ("call_to_action", app_blocks.LargeCallToActionBlock()),
            ("gallery_of_calls_to_action", app_blocks.CallToActionGalleryBlock()),
            ("metrics", app_blocks.MetricsBlock()),
            ("html", app_blocks.HTMLBlock()),
            ("partner_logos", app_blocks.PartnerLogos()),
            ("latest_articles", app_blocks.LatestArticles()),
            ("featured_projects", app_blocks.FeaturedProjects()),
        ],
        null=True,
        blank=True,
        use_json_field=True,
    )

    # Fields
    sidebar = StreamField(
        [
            ("richtext", blocks.RichTextBlock(group="Basic")),
            ("image", app_blocks.ImageBlock()),
            ("call_to_action", app_blocks.SimpleCallToActionBlock()),
        ],
        null=True,
        blank=True,
        use_json_field=True,
    )

    # Editor
    content_page_panels = [
        FieldPanel("content"),
        FieldPanel("sidebar"),
    ]
    content_panels = PreviewablePage.content_panels + content_page_panels

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(Page.promote_panels, heading="Sharing"),
            ObjectList(
                Page.settings_panels,
                heading="Publishing Schedule",
                classname="settings",
            ),
        ]
    )


class SearchableDirectoryMixin(Page):
    search_highlight_field = "content"
    per_page = 9

    class Meta:
        abstract = True

    def get_search_query(self, request):
        return request.GET.get("query")

    def get_queryset(self):
        return self.get_children().live().public()

    def do_search(self, request):
        search_query = self.get_search_query(request)

        if search_query:
            query = Query.get(search_query)
            query.add_hit()

            return self.get_queryset().search(search_query)
        else:
            return self.get_queryset()

    def get_search_highlight(self, request, page):
        if hasattr(page, self.search_highlight_field):
            highlighter = SearchHeadline(
                self.search_highlight_field,
                query=SearchQuery(self.get_search_query(request)),
                min_words=60,
                max_words=80,
                start_sel="<cksearch:hl>",
                stop_sel="</cksearch:hl>",
            )

            highlights_raw = (
                type(page)
                .objects.annotate(search_highlight=highlighter)
                .get(id=page.id)
                .search_highlight
            )

            highlight_groups = list(
                hl.split("</cksearch:hl>")
                for hl in highlights_raw.split("<cksearch:hl>")
            )
            start = highlight_groups.pop(0)[0]

            highlights = tuple(
                format_html(
                    '<span class="search-highlight">{}</span>{}',
                    mark_safe(highlight),
                    next,
                )
                for highlight, next in highlight_groups
            )

            return concat_html(start, *highlights)

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        search_results = list({p.specific.localized for p in self.do_search(request)})
        paginator = Paginator(search_results, self.per_page)
        current_page_number = max(
            1, min(paginator.num_pages, safe_to_int(request.GET.get("page"), 1))
        )
        paginator_page = paginator.page(current_page_number)

        context.update(
            {
                "search_query": self.get_search_query(request),
                "search_results": lambda: [
                    {
                        "page": page,
                        "search_highlight": lambda: self.get_search_highlight(
                            request, page.specific
                        ),
                    }
                    for page in paginator_page
                ],
                "pages": lambda: [page.specific for page in paginator_page],
                "total_count": paginator.count,
                "paginator_page": paginator_page,
                "paginator": paginator,
            }
        )

        return context


class GeocodedMixin(Page):
    """
    Common configuration for pages that want to track a geographical location.
    """

    class Meta:
        abstract = True

    geographical_location = models.CharField(max_length=250, null=True, blank=True)
    coordinates = PointField(null=True, blank=True)
    related_countries = ParentalManyToManyField("app.CountryPage", blank=True)

    @property
    def localized_related_countries(self):
        """
        Translations of this page might have different foreign keys defined
        so collect them all up
        """
        return localized_related_pages(self, "related_countries")

    @property
    def has_unique_location(self):
        return self.coordinates is not None

    @property
    def centroid(self):
        if self.coordinates is not None:
            return self.coordinates
        related_country = self.related_countries.first()
        if related_country is not None:
            return related_country.centroid

    @property
    def longitude(self):
        if self.centroid:
            return self.centroid.coords[0]

    @property
    def latitude(self):
        if self.centroid:
            return self.centroid.coords[1]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # For comparison purposes
        self.__previous_coordinates = self.coordinates

    @property
    def has_coordinates(self):
        return self.latitude is not None

    @property
    def map_image_url(self):
        if self.featured_image is not None:
            rendition = self.featured_image.get_rendition("fill-140x140|jpegquality-80")
            return rendition.full_url

    def save(self, *args, **kwargs):
        try:
            coordinates_changed = self.__previous_coordinates != self.coordinates
            if self.has_coordinates is True and self.geographical_location is None:
                self.update_location_name()
        except:
            pass
        super().save(*args, **kwargs)

    def update_location_name(self):
        if self.coordinates is not None:
            location_data = geolocator.reverse(self.coordinates, zoom=5, exactly_one=1)
            if location_data is not None:
                self.geographical_location = location_data.address

    content_panels = [
        MultiFieldPanel(
            [
                AutocompletePanel("related_countries", target_model="app.CountryPage"),
                FieldPanel("geographical_location"),
                FieldPanel("coordinates", widget=MapboxPointFieldWidget),
            ],
            heading="Geographic location",
        )
    ]

    @classmethod
    def label(self):
        return self._meta.verbose_name.removesuffix(" page")

    api_fields = [
        APIField("label"),
        APIField("geographical_location"),
        APIField("countries"),
    ]

    # Make the slug synchronised, but don't allow it to be overridden on translations
    override_translatable_fields = [
        SynchronizedField("geographical_location", overridable=False),
        SynchronizedField("coordinates", overridable=False),
        SynchronizedField("related_countries", overridable=False),
    ]


class IconMixin(Page):
    class Meta:
        abstract = True

    icon_dark_transparent = models.ForeignKey(
        CMSImage,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="For use on top of light/white backgrounds",
    )
    icon_light_transparent = models.ForeignKey(
        CMSImage,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="For use on top of dark/colourful backgrounds",
    )

    icon_panels = [
        MultiFieldPanel(
            [FieldPanel("icon_dark_transparent"), FieldPanel("icon_light_transparent")],
            heading="Page icon",
        )
    ]

    # Make the slug synchronised, but don't allow it to be overridden on translations
    override_translatable_fields = [
        SynchronizedField("icon_dark_transparent", overridable=False),
        SynchronizedField("icon_light_transparent", overridable=False),
    ]


class ThemeablePageMixin(Page):
    class Meta:
        abstract = True

    class ThemeColourChoices(models.TextChoices):
        blue = "theme-blue", "blue"
        red = "theme-red", "red"
        yellow = "theme-yellow", "yellow"
        orange = "theme-orange", "orange"
        pink = "theme-pink", "pink"
        purple = "theme-purple", "purple"
        indigo = "theme-indigo", "indigo"
        teal = "theme-teal", "teal"
        green = "theme-green", "green"
        gray = "theme-gray", "gray"

    theme_class = models.CharField(
        max_length=50,
        choices=ThemeColourChoices.choices,
        default=ThemeColourChoices.blue,
        verbose_name="Theme colour",
        help_text="Pick the colour palette for this page's elements. Defaults to HOT blue.",
    )

    themeable_content_panels = [FieldPanel("theme_class")]

    # Make the slug synchronised, but don't allow it to be overridden on translations
    override_translatable_fields = [
        SynchronizedField("theme_class", overridable=False),
    ]


class RelatedImpactAreaMixin(Page):
    class Meta:
        abstract = True

    related_impact_areas = ParentalManyToManyField("app.ImpactAreaPage", blank=True)

    content_panels = [
        AutocompletePanel("related_impact_areas", target_model="app.ImpactAreaPage")
    ]

    @property
    def localized_related_impact_areas(self):
        """
        Translations of this page might have different foreign keys defined
        so collect them all up
        """
        return localized_related_pages(self, "related_impact_areas")

    # Make the slug synchronised, but don't allow it to be overridden on translations
    override_translatable_fields = [
        SynchronizedField("related_impact_areas", overridable=False),
    ]

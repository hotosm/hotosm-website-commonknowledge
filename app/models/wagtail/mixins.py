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
from wagtailautocomplete.edit_handlers import AutocompletePanel

import app.models.wagtail.blocks as app_blocks
from app.helpers import concat_html, safe_to_int

# from app.serializers import PageCoordinatesSerializer
from app.utils.geo import geolocator

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

    @property
    def label(self):
        return self._meta.verbose_name.removesuffix(" page")

    # Editor
    content_panels = Page.content_panels + [
        FieldPanel("short_summary"),
        FieldPanel("featured_image"),
        # FieldPanel("frontmatter"),
    ]

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
        [
            ("richtext", blocks.RichTextBlock()),
            ("image", app_blocks.ImageBlock()),
            ("cta", app_blocks.CallToActionBlock()),
            ("page_link", app_blocks.PageLinkBlock()),
            ("page_gallery", app_blocks.PageLinkGalleryBlock()),
            ("cta_gallery", app_blocks.CallToActionGalleryBlock()),
            ("featured_content", app_blocks.FeaturedContentBlock()),
            ("metrics", app_blocks.MetricsBlock()),
            ("people_gallery", app_blocks.RelatedPeopleBlock()),
            ("map", app_blocks.MapBlock()),
            ("html", app_blocks.HTMLBlock()),
        ],
        null=True,
        blank=True,
        use_json_field=True,
    )

    # Editor
    content_panels = PreviewablePage.content_panels + [
        FieldPanel("content"),
    ]

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


class ContentSidebarPage(ContentPage):
    class Meta:
        abstract = True

    # Fields
    sidebar = StreamField(
        [
            ("richtext", blocks.RichTextBlock()),
            ("image", app_blocks.ImageBlock()),
            ("page_link", app_blocks.PageLinkBlock()),
            ("featured_content", app_blocks.FeaturedContentBlock()),
        ],
        null=True,
        blank=True,
        use_json_field=True,
    )

    # Editor
    content_panels = ContentPage.content_panels + [
        FieldPanel("sidebar"),
    ]

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
    # map_image = models.ForeignKey(
    #     CMSImage, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')

    @property
    def centroid(self):
        related_country = self.related_countries.first()
        if self.coordinates is not None:
            return self.coordinates
        elif related_country is not None:
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

    def save(self, *args, **kwargs):
        try:
            coordinates_changed = self.__previous_coordinates != self.coordinates
            if self.has_coordinates is True and self.geographical_location is None:
                self.update_location_name()
            # if self.has_coordinates is True and (self.map_image is None or coordinates_changed):
            #     self.update_map_thumbnail()
        except:
            pass
        super().save(*args, **kwargs)

    def update_location_name(self):
        if self.coordinates is not None:
            location_data = geolocator.reverse(self.coordinates, zoom=5, exactly_one=1)
            if location_data is not None:
                self.geographical_location = location_data.address

    # def update_map_thumbnail(self):
    #     if self.coordinates is None:
    #         return
    #     url = self.static_map_marker_image_url()
    #     if url is None:
    #         return
    #     response = requests.get(url)
    #     if response.status_code != 200:
    #         print("Map generator error:", url)
    #         print(response.status_code, response.content)
    #         return
    #     image = ImageFile(BytesIO(response.content),
    #                       name=f'{urllib.parse.quote(url)}.png')

    #     if self.map_image is not None:
    #         self.map_image.delete()

    #     self.map_image = CmsImage(
    #         alt_text=f"Map of {self.geographical_location}",
    #         title=f'Generated map thumbnail for {self._meta.model_name} {self.slug}',
    #         file=image
    #     )
    #     self.map_image.save()

    # def static_map_marker_image_url(self) -> str:
    #     return static_map_marker_image_url(
    #         self.coordinates,
    #         access_token=settings.MAPBOX_API_PUBLIC_TOKEN,
    #         marker_url=self.map_marker,
    #         username='smartforests',
    #         style_id='ckziehr6u001e14ohgl2brzlu',
    #         width=300,
    #         height=200,
    #     )

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
        # APIField("coordinates", serializer=PageCoordinatesSerializer),
        APIField("countries"),
    ]

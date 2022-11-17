import json
import re
from unicodedata import lookup

import pycountry
from bs4 import BeautifulSoup
from django.contrib.gis.geos import GEOSGeometry, Point
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify
from django.utils.translation import get_language_from_request
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from taggit.models import ItemBase, TagBase
from wagtail import blocks
from wagtail.admin.panels import FieldPanel, FieldRowPanel, ObjectList, TabbedInterface
from wagtail.core.rich_text import RichText
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page
from wagtail.snippets.models import register_snippet

import app.models.wagtail.blocks as app_blocks
from app.models.wagtail.mixins import (
    ContentPage,
    ContentSidebarPage,
    GeocodedMixin,
    PreviewablePage,
    SearchableDirectoryMixin,
)
from app.utils.cache import django_cached
from app.utils.geo import geolocator

from .cms import CMSImage

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


def monkey_patch_richtext():
    # We'll be wrapping the original RichText.__html__(), so make
    # sure we have a reference to it that we can call.
    __original__html__ = RichText.__html__

    def with_heading_ids(self):
        """
        We don't actually change how RichText.__html__ works, we just replace
        it with a function that does "whatever it already did", plus a
        substitution pass that adds fragment ids and their associated link
        elements to any headings that might be in the rich text content.
        """
        html = __original__html__(self)
        soup = BeautifulSoup(html, "lxml")
        for heading in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
            heading["id"] = slugify(heading.get_text())
        return soup.prettify()

    # Rebind the RichText's html serialization function such that
    # the output is still entirely functional as far as wagtail
    # can tell, except with headings enriched with fragment ids.
    RichText.__html__ = with_heading_ids


@register_snippet
class HOTOSMTag(TagBase):
    pass


class HomePage(SearchableDirectoryMixin, Page):
    max_count_per_parent = 1
    page_description = "Website home page. Should only be one such page per locale."
    parent_page_type = []
    show_in_menus_default = False
    content = StreamField(
        [
            ("richtext", blocks.RichTextBlock()),
            ("html", app_blocks.HTMLBlock()),
            ("metrics", app_blocks.MetricsBlock()),
            ("image", app_blocks.ImageBlock()),
            ("featured_content", app_blocks.FeaturedContentBlock()),
            ("cta", app_blocks.CallToActionBlock()),
            ("page_link", app_blocks.PageLinkBlock()),
            ("page_gallery", app_blocks.PageLinkGalleryBlock()),
            ("cta_gallery", app_blocks.CallToActionGalleryBlock()),
            ("people_gallery", app_blocks.RelatedPeopleBlock()),
            ("heading_and_subheading", app_blocks.HeadingAndSubHeadingBlock()),
            ("partner_logos", app_blocks.PartnerLogos()),
            ("map", app_blocks.MapBlock()),
        ],
        null=True,
        blank=True,
        use_json_field=True,
    )
    content_panels = Page.content_panels + [FieldPanel("content")]

    template = "app/directory.html"


def validate_genuine_isoa2_code(value):
    country = pycountry.countries.get(alpha_2=value)
    if country is None:
        raise ValidationError("Must be a valid ISO Alpha 2 country code")


def validate_genuine_isoa3_code(value):
    if value is None or value == "":
        return
    country = pycountry.countries.get(alpha_3=value)
    if country is None:
        raise ValidationError("Must be a valid ISO Alpha 3 country code")


@register_snippet
class CountryPage(ContentPage):
    class Meta:
        ordering = ["title"]

    parent_page_type = ["app.DirectoryPage"]
    page_description = "Page for each country"
    isoa2 = models.CharField(
        max_length=2,
        unique=True,
        validators=[validate_genuine_isoa2_code],
        help_text="ISO Alpha 2 country code",
    )
    isoa3 = models.CharField(
        max_length=3,
        unique=True,
        validators=[validate_genuine_isoa3_code],
        blank=True,
        null=True,
        help_text="ISO Alpha 3 country code",
    )
    continent = models.CharField(max_length=50, blank=True, null=True)

    # Editor
    content_panels = Page.content_panels + [
        FieldRowPanel(
            [
                FieldPanel("isoa2"),
                FieldPanel("isoa3"),
                FieldPanel("continent"),
            ],
            heading="Metadata",
        ),
        FieldPanel("featured_image"),
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

    # Methods
    @property
    def metadata(self):
        return pycountry.countries.get(alpha_2=self.isoa2)

    @classmethod
    def search_fuzzy(cls, name_or_code: str):
        results = pycountry.countries.search_fuzzy(name_or_code)
        if len(results) > 0:
            return results[0]

    @classmethod
    def create_for_code(cls, isoa2: str):
        metadata = pycountry.countries.get(alpha_2=isoa2)
        return CountryPage(
            title=metadata.name,
            slug=slugify(metadata.name),
            isoa2=metadata.alpha_2,
            isoa3=metadata.alpha_3,
        )

    @property
    @django_cached("country_geocode", get_key=lambda self: self.isoa2)
    def geo(self):
        return geolocator.geocode(
            self.isoa2,
            exactly_one=True,
            geometry="geojson",
            country_codes=self.isoa2.lower(),
            featuretype="country",
        )

    @property
    @django_cached("country_coordinates", get_key=lambda self: self.isoa2)
    def centroid(self):
        # TODO: More intelligent centroids available from https://raw.githubusercontent.com/gavinr/world-countries-centroids/29c9d1ec9013b6b36e3f6cf3634daaffd8afb2ea/dist/countries.geojson
        return Point(self.geo.longitude, self.geo.latitude, self.geo.altitude)

    @property
    @django_cached("country_geometry", get_key=lambda self: self.isoa2)
    def geometry(self):
        return GEOSGeometry(json.dumps(self.geo.raw.get("geojson")))

    @property
    def emoji_flag(self):
        return lookup(f"REGIONAL INDICATOR SYMBOL LETTER {self.isoa2[0]}") + lookup(
            f"REGIONAL INDICATOR SYMBOL LETTER {self.isoa2[1]}"
        )

    def autocomplete_label(self):
        return f"{self.emoji_flag} {self.title}"


class StaticPage(ContentSidebarPage):
    class Meta:
        ordering = ["title"]

    page_description = "Use this for generic longform text. Use Landing Page if you need full width, freeform content instead."

    # Layout
    show_table_of_contents = models.BooleanField(default=True)
    show_section_navigation = models.BooleanField(default=False)
    show_breadcrumb = models.BooleanField(default=True)
    layout_panels = [
        FieldPanel("show_table_of_contents"),
        # FieldPanel("show_section_navigation"),
        FieldPanel("show_breadcrumb"),
    ]
    edit_handler = TabbedInterface(
        [
            ObjectList(ContentSidebarPage.content_panels, heading="Content"),
            ObjectList(layout_panels, heading="Layout"),
            ObjectList(ContentSidebarPage.promote_panels, heading="Sharing"),
            ObjectList(
                ContentSidebarPage.settings_panels,
                heading="Publishing Schedule",
                classname="settings",
            ),
        ]
    )


class LandingPage(ContentPage):
    class Meta:
        ordering = ["title"]

    page_description = (
        "Use this to construct freeform pages. Use Static Page for longform text."
    )

    # Layout
    show_header = models.BooleanField(default=True)
    show_footer = models.BooleanField(default=True)
    layout_panels = [
        FieldPanel("show_header"),
        FieldPanel("show_footer"),
    ]
    edit_handler = TabbedInterface(
        [
            ObjectList(ContentPage.content_panels, heading="Content"),
            ObjectList(layout_panels, heading="Layout"),
            ObjectList(ContentPage.promote_panels, heading="Sharing"),
            ObjectList(
                ContentPage.settings_panels,
                heading="Publishing Schedule",
                classname="settings",
            ),
        ]
    )


class TaggedProject(ItemBase):
    tag = models.ForeignKey(
        HOTOSMTag, related_name="tagged_projects", on_delete=models.CASCADE
    )
    content_object = ParentalKey(
        to="app.ProjectPage", on_delete=models.CASCADE, related_name="tagged_projects"
    )


@register_snippet
class ProjectPage(GeocodedMixin, ContentSidebarPage):
    class Meta:
        ordering = ["-first_published_at"]

    parent_page_type = ["app.DirectoryPage"]
    template = "app/static_page.html"
    page_description = "HOTOSM and third party projects"
    tags = ClusterTaggableManager(through=TaggedProject, blank=True)
    # TODO: project status

    # Editor
    content_panels = ContentSidebarPage.content_panels + [
        FieldPanel("tags"),
        *GeocodedMixin.content_panels,
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


class DirectoryPage(SearchableDirectoryMixin, PreviewablePage):
    page_description = (
        "A directory to store lists of things, like projects or people or organisations"
    )

    template = "app/directory.html"


class PersonType(TagBase):
    pass


class TaggedPerson(ItemBase):
    tag = models.ForeignKey(
        PersonType, related_name="tagged_people", on_delete=models.CASCADE
    )
    content_object = ParentalKey(
        to="app.PersonPage", on_delete=models.CASCADE, related_name="tagged_people"
    )


@register_snippet
class PersonPage(GeocodedMixin, ContentPage):
    class Meta:
        ordering = ["title"]

    parent_page_type = ["app.DirectoryPage"]

    # Editor
    template = "app/static_page.html"
    page_description = "Contributors, staff, and other people"
    category = ClusterTaggableManager(through=TaggedPerson, blank=True)
    # TODO: relations
    # TODO: external links

    content_panels = ContentPage.content_panels + [*GeocodedMixin.content_panels]

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


class TaggedOrganisation(ItemBase):
    tag = models.ForeignKey(
        HOTOSMTag, related_name="tagged_organisations", on_delete=models.CASCADE
    )
    content_object = ParentalKey(
        to="app.OrganisationPage",
        on_delete=models.CASCADE,
        related_name="tagged_organisations",
    )


class OrganisationPage(GeocodedMixin, ContentPage):
    class Meta:
        ordering = ["title"]

    parent_page_type = ["app.DirectoryPage"]
    template = "app/static_page.html"
    page_description = "Internal and external organisations"
    tags = ClusterTaggableManager(through=TaggedOrganisation, blank=True)

    # Editor
    content_panels = ContentPage.content_panels + [
        FieldPanel("tags"),
        *GeocodedMixin.content_panels,
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


class OpportunityType(TagBase):
    pass


class TaggedOpportunity(ItemBase):
    tag = models.ForeignKey(
        OpportunityType, related_name="tagged_people", on_delete=models.CASCADE
    )

    content_object = ParentalKey(
        to="app.OpportunityPage", on_delete=models.CASCADE, related_name="tagged_people"
    )


@register_snippet
class OpportunityPage(GeocodedMixin, ContentPage):
    class Meta:
        ordering = ["-first_published_at"]

    parent_page_type = ["app.DirectoryPage"]
    template = "app/static_page.html"
    page_description = "Opportunities for people to get involved with HOT"
    deadline_datetime = models.DateTimeField(blank=True, null=True)
    place_of_work = models.CharField(max_length=1000, blank=True, null=True)
    apply_form_url = models.URLField(blank=True, null=True)
    category = ClusterTaggableManager(through=TaggedOpportunity, blank=True)

    # Editor
    content_panels = ContentPage.content_panels + [
        FieldPanel("deadline_datetime"),
        FieldPanel("place_of_work"),
        FieldPanel("apply_form_url"),
        *GeocodedMixin.content_panels,
    ]


class MagazineIndexPage(SearchableDirectoryMixin, PreviewablePage):
    page_description = "Home page for the magazine section of the site"
    show_in_menus_default = True
    max_count_per_parent = 1
    parent_page_type = ["app.HomePage"]
    subpage_types = [
        "app.ArticlePage",
    ]
    # TODO: Featured articles
    # TODO: Sections

    def get_queryset(self):
        return ArticlePage.objects.descendant_of(self).order_by("-first_published_at")


class TaggedArticle(ItemBase):
    tag = models.ForeignKey(
        HOTOSMTag, related_name="tagged_articles", on_delete=models.CASCADE
    )
    content_object = ParentalKey(
        to="app.ArticlePage", on_delete=models.CASCADE, related_name="tagged_articles"
    )


class MagazineSection(SearchableDirectoryMixin, PreviewablePage):
    page_description = "A section of the magazine"
    parent_page_type = ["app.MagazineIndexPage", "app.HomePage"]
    subpage_types = ["app.ArticlePage", "app.MagazineSection"]
    show_in_menus_default = True
    template = "app/magazine_index_page.html"

    def get_queryset(self):
        return ArticlePage.objects.descendant_of(self).order_by("-first_published_at")


@register_snippet
class ArticlePage(GeocodedMixin, ContentSidebarPage):
    class Meta:
        ordering = ["-first_published_at"]

    template = "app/static_page.html"
    page_description = "Blog posts, news reports, updates and so on"
    parent_page_type = ["app.MagazineIndexPage", "app.MagazineSection"]
    show_in_menus_default = False

    tags = ClusterTaggableManager(through=TaggedArticle, blank=True)

    # Editor
    metadata_panels = [FieldPanel("tags"), *GeocodedMixin.content_panels]

    edit_handler = TabbedInterface(
        [
            ObjectList(ContentSidebarPage.content_panels, heading="Content"),
            ObjectList(metadata_panels, heading="Metadata"),
            ObjectList(Page.promote_panels, heading="Sharing"),
            ObjectList(
                Page.settings_panels,
                heading="Publishing Schedule",
                classname="settings",
            ),
        ]
    )


class TopicContextMixin:
    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        language_code = get_language_from_request(request)

        context.update(
            {
                "current_topic": self.get_ancestors(inclusive=True)
                .type(TopicHomepage)
                .first(),
                "all_tags": TopicHomepage.objects.filter(
                    locale__language_code=language_code
                )
                .live()
                .public()
                .in_menu()
                .all(),
            }
        )
        return context


class TopicHomepage(TopicContextMixin, ContentPage):
    template = "app/topic_homepage.html"

    page_description = "Topical overview, can contain subpages"
    subpage_types = ["app.TopicPage"]

    # Layout
    show_table_of_contents = models.BooleanField(default=True)
    show_section_navigation = models.BooleanField(default=True)
    show_breadcrumb = models.BooleanField(default=True)
    layout_panels = [
        FieldPanel("show_table_of_contents"),
        FieldPanel("show_section_navigation"),
        FieldPanel("show_breadcrumb"),
    ]
    edit_handler = TabbedInterface(
        [
            ObjectList(ContentPage.content_panels, heading="Content"),
            ObjectList(layout_panels, heading="Layout"),
            ObjectList(ContentPage.promote_panels, heading="Sharing"),
            ObjectList(
                ContentPage.settings_panels,
                heading="Publishing Schedule",
                classname="settings",
            ),
        ]
    )


class TaggedTopic(ItemBase):
    tag = models.ForeignKey(
        HOTOSMTag, related_name="tagged_tags", on_delete=models.CASCADE
    )
    content_object = ParentalKey(
        to="app.TopicPage", on_delete=models.CASCADE, related_name="tagged_tags"
    )


@register_snippet
class TopicPage(TopicContextMixin, ContentPage):
    template = "app/topic_page.html"

    page_description = "Guide / resource page for a specific task or question."
    parent_page_type = ["app.TopicHomepage", "app.TopicPage"]
    subpage_types = ["app.TopicPage"]

    # Fields
    tags = ClusterTaggableManager(through=TaggedTopic, blank=True)

    content_panels = ContentPage.content_panels + [
        FieldPanel("tags"),
    ]

    # Layout
    show_table_of_contents = models.BooleanField(default=True)
    show_section_navigation = models.BooleanField(default=True)
    show_breadcrumb = models.BooleanField(default=True)
    layout_panels = [
        FieldPanel("show_table_of_contents"),
        FieldPanel("show_section_navigation"),
        FieldPanel("show_breadcrumb"),
    ]
    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(layout_panels, heading="Layout"),
            ObjectList(ContentPage.promote_panels, heading="Sharing"),
            ObjectList(
                ContentPage.settings_panels,
                heading="Publishing Schedule",
                classname="settings",
            ),
        ]
    )


class TaggedEvent(ItemBase):
    tag = models.ForeignKey(
        HOTOSMTag, related_name="tagged_events", on_delete=models.CASCADE
    )
    content_object = ParentalKey(
        to="app.EventPage", on_delete=models.CASCADE, related_name="tagged_events"
    )


@register_snippet
class EventPage(GeocodedMixin, ContentPage):
    template = "app/static_page.html"
    page_description = "Events, workshops, and other gatherings"

    class Meta:
        ordering = ["start_datetime"]

    # Fields
    start_datetime = models.DateTimeField(null=False, blank=False)
    end_datetime = models.DateTimeField(null=True, blank=True)
    tags = ClusterTaggableManager(through=TaggedEvent, blank=True)

    # Editor
    content_panels = ContentPage.content_panels + [
        FieldRowPanel(
            [
                FieldPanel("start_datetime"),
                FieldPanel("end_datetime"),
            ],
            heading="Scheduling",
        ),
        *GeocodedMixin.content_panels,
        FieldPanel("tags"),
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(Page.promote_panels, heading="Sharing"),
            ObjectList(
                Page.settings_panels,
                heading="Page publishing schedule",
                classname="settings",
            ),
        ]
    )

    # Logic
    def clean(self):
        """Clean the model fields, if end_datetime is before start_datetime raise a ValidationError."""
        super().clean()
        if self.end_datetime:
            if self.end_datetime < self.start_datetime:
                raise ValidationError(
                    {"end_datetime": "The end date cannot be before the start date."}
                )


class ActivationIndexPage(PreviewablePage):
    template = "app/static_page.html"
    page_description = "Home page for the activations section of the site"
    show_in_menus_default = True
    max_count_per_parent = 1
    parent_page_type = ["app.HomePage"]
    subpage_types = [
        "app.ActivationProjectPage",
    ]


@register_snippet
class ActivationProjectPage(ContentPage):
    template = "app/static_page.html"
    parent_page_type = ["app.ActivationIndexPage"]
    page_description = "Disaster Services activation projects"

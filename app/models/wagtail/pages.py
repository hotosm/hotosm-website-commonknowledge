import re

from bs4 import BeautifulSoup
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify
from django.utils.translation import get_language_from_request
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from taggit.models import ItemBase, TagBase
from wagtail import blocks
from wagtail.admin.panels import (
    FieldPanel,
    MultiFieldPanel,
    ObjectList,
    TabbedInterface,
)
from wagtail.core.rich_text import RichText
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page

import app.models.wagtail.blocks as app_blocks

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


class HOTOSMTag(TagBase):
    pass


class HomePage(Page):
    max_count_per_parent = 1
    page_description = "Website home page. Should only be one such page per locale."
    parent_page_type = []
    show_in_menus_default = False
    content = StreamField(
        [
            ("links_section", app_blocks.HomepageSectionBlock()),
            ("map_section", app_blocks.HomepageMapBlock()),
            ("magazine_section", app_blocks.HomepageMagazineBlock()),
            ("summary_text", app_blocks.PageSummaryBlock()),
            ("richtext", blocks.RichTextBlock()),
        ],
        null=True,
        blank=True,
        use_json_field=True,
    )
    content_panels = Page.content_panels + [FieldPanel("content")]


class PreviewablePage(Page):
    class Meta:
        abstract = True

    # Fields
    featured_image = models.ForeignKey(
        CMSImage,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    image_url = models.URLField(
        blank=True,
        null=True,
        help_text="If set, this image will be used instead of the featured image.",
    )
    short_summary = models.CharField(max_length=1500, blank=True, null=True)
    frontmatter = models.JSONField(
        blank=True, null=True, help_text="Metadata from the legacy site"
    )

    # Editor
    content_panels = Page.content_panels + [
        FieldPanel("short_summary"),
        MultiFieldPanel(
            [
                FieldPanel("featured_image"),
                FieldPanel("image_url"),
            ],
            heading="Imagery",
        ),
        FieldPanel("frontmatter"),
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

    template = "app/static_page.html"

    # Fields
    content = StreamField(
        [
            ("richtext", blocks.RichTextBlock()),
            ("embeddable_code", app_blocks.HTMLBlock()),
            ("links_gallery", app_blocks.GuideSection()),
            ("featured_link", app_blocks.FeaturedLinkBlock()),
            ("simple_link", app_blocks.LinkBlock()),
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


class StaticPage(ContentSidebarPage):
    page_description = "General information page"

    # Layout
    show_header = models.BooleanField(default=True)
    show_footer = models.BooleanField(default=True)
    show_table_of_contents = models.BooleanField(default=True)
    show_section_navigation = models.BooleanField(default=False)
    show_breadcrumb = models.BooleanField(default=True)
    layout_panels = [
        FieldPanel("show_header"),
        FieldPanel("show_footer"),
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


class TaggedProject(ItemBase):
    tag = models.ForeignKey(
        HOTOSMTag, related_name="tagged_projects", on_delete=models.CASCADE
    )
    content_object = ParentalKey(
        to="app.ProjectPage", on_delete=models.CASCADE, related_name="tagged_projects"
    )


class ProjectPage(ContentSidebarPage):
    page_description = "HOTOSM and third party projects"
    tags = ClusterTaggableManager(through=TaggedProject, blank=True)
    # TODO: relations
    # TODO: project status

    content_panels = ContentSidebarPage.content_panels + [
        FieldPanel("tags"),
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


class DirectoryPage(PreviewablePage):
    page_description = (
        "A directory to store lists of things, like projects or people or organisations"
    )


class PersonType(TagBase):
    pass


class TaggedPerson(ItemBase):
    tag = models.ForeignKey(
        PersonType, related_name="tagged_people", on_delete=models.CASCADE
    )
    content_object = ParentalKey(
        to="app.PersonPage", on_delete=models.CASCADE, related_name="tagged_people"
    )


class PersonPage(ContentPage):
    page_description = "Contributors, staff, and other people"
    category = ClusterTaggableManager(through=TaggedPerson, blank=True)
    # TODO: relations
    # TODO: external links


class TaggedOrganisation(ItemBase):
    tag = models.ForeignKey(
        HOTOSMTag, related_name="tagged_organisations", on_delete=models.CASCADE
    )
    content_object = ParentalKey(
        to="app.OrganisationPage",
        on_delete=models.CASCADE,
        related_name="tagged_organisations",
    )


class OrganisationPage(ContentPage):
    page_description = "Internal and external organisations"
    tags = ClusterTaggableManager(through=TaggedOrganisation, blank=True)

    content_panels = ContentPage.content_panels + [
        FieldPanel("tags"),
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


class OpportunityPage(ContentPage):
    page_description = "Opportunities for people to get involved with HOT"
    deadline_datetime = models.DateTimeField(blank=True, null=True)
    place_of_work = models.CharField(max_length=1000, blank=True, null=True)
    apply_form_url = models.URLField(blank=True, null=True)
    category = ClusterTaggableManager(through=TaggedOpportunity, blank=True)

    content_panels = ContentPage.content_panels + [
        FieldPanel("deadline_datetime"),
        FieldPanel("place_of_work"),
        FieldPanel("apply_form_url"),
    ]


class MagazineIndexPage(PreviewablePage):
    page_description = "Home page for the magazine section of the site"
    show_in_menus_default = True
    max_count_per_parent = 1
    parent_page_type = ["app.HomePage"]
    subpage_types = [
        "app.ArticlePage",
    ]
    # TODO: Featured articles
    # TODO: Sections


class TaggedArticle(ItemBase):
    tag = models.ForeignKey(
        HOTOSMTag, related_name="tagged_articles", on_delete=models.CASCADE
    )
    content_object = ParentalKey(
        to="app.ArticlePage", on_delete=models.CASCADE, related_name="tagged_articles"
    )


class MagazineSection(PreviewablePage):
    page_description = "A section of the magazine"
    parent_page_type = ["app.MagazineIndexPage"]
    subpage_types = ["app.ArticlePage", "app.MagazineSection"]
    show_in_menus_default = True


class ArticlePage(ContentSidebarPage):
    page_description = "Blog posts, news reports, updates and so on"
    parent_page_type = ["app.MagazineIndexPage", "app.MagazineSection"]
    show_in_menus_default = False

    tags = ClusterTaggableManager(through=TaggedArticle, blank=True)

    content_panels = ContentSidebarPage.content_panels + [
        FieldPanel("tags"),
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


class EventPage(ContentPage):
    page_description = "Events, workshops, and other gatherings"

    class Meta:
        ordering = ["start_datetime"]

    # Fields
    start_datetime = models.DateTimeField(null=False, blank=False)
    end_datetime = models.DateTimeField(null=True, blank=True)
    tags = ClusterTaggableManager(through=TaggedEvent, blank=True)

    # Editor
    content_panels = ContentPage.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("start_datetime"),
                FieldPanel("end_datetime"),
            ],
            heading="Event Details",
        ),
        FieldPanel("tags"),
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
    page_description = "Home page for the activations section of the site"
    show_in_menus_default = True
    max_count_per_parent = 1
    parent_page_type = ["app.HomePage"]
    subpage_types = [
        "app.ActivationProjectPage",
    ]


class ActivationProjectPage(ContentPage):
    parent_page_type = ["app.ActivationIndexPage"]
    page_description = "Disaster Services activation projects"

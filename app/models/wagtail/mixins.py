from math import ceil

from django.contrib.postgres.search import SearchHeadline, SearchQuery
from django.core.paginator import Paginator
from django.db import models
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.core.models import Page
from wagtail.search.models import Query

from app.helpers import concat_html, safe_to_int

from .cms import CMSImage


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

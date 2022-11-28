# View for the block, that takes URL query params (?page_type=…&category=…&sort=…) and outputs the queryset, other template context, renders the template

import datetime

from django import forms
from django.contrib.postgres.search import SearchHeadline, SearchQuery
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.views.generic import TemplateView
from wagtail.core.models import Page
from wagtail.search.models import Query

from app.helpers import concat_html, safe_to_int
from app.models import (
    ArticlePage,
    CountryPage,
    EventPage,
    GeocodedMixin,
    ImpactAreaPage,
    OpportunityPage,
    OrganisationPage,
    PersonPage,
    ProjectPage,
    RelatedImpactAreaMixin,
)
from app.utils.python import ensure_1D_list
from app.utils.wagtail import abstract_page_query_filter


class DirectoryView(TemplateView):
    template_name = "app/include/frames/directory.html"
    page_model = Page
    search_highlight_field = "content"
    per_page = 9

    page_types = {
        "projects": ProjectPage,
        "organisations": OrganisationPage,
        "people": PersonPage,
        "events": EventPage,
        "opportunities": OpportunityPage,
        "news": ArticlePage,
    }

    filters = [
        {
            "url_param": "year",
            "label": "Year",
            "widget": "dropdown",
            "options": lambda: range(2010, datetime.date.today().year + 1),
            "query": lambda qs, values: qs.filter(
                Q(
                    first_published_at__year__in=map(
                        lambda v: int(v), ensure_1D_list(values)
                    )
                )
                | Q(
                    last_published_at__year__in=map(
                        lambda v: int(v), ensure_1D_list(values)
                    )
                )
            ),
        },
        {
            "url_param": "impact_area",
            "label": "Impact Areas",
            "widget": "dropdown",
            "options": lambda: ImpactAreaPage.objects.live()
            .public()
            .all()
            .order_by("title"),
            "query": lambda qs, values: qs.filter(
                abstract_page_query_filter(
                    RelatedImpactAreaMixin,
                    dict(related_impact_areas__in=ensure_1D_list(values)),
                )
            ),
        },
        {
            "url_param": "country",
            "label": "Countries",
            "widget": "dropdown",
            "options": lambda: CountryPage.objects.live()
            .public()
            .all()
            .order_by("title"),
            "query": lambda qs, values: qs.filter(
                abstract_page_query_filter(
                    GeocodedMixin,
                    dict(related_countries__isoa2__in=ensure_1D_list(values)),
                )
            ),
        },
    ]

    def current_filters(self, request):
        return [
            {**filter, "current_value": request.GET.get(filter["url_param"], None)}
            for filter in self.filters
        ]

    def get_queryset(self):
        qs = Page.objects.live().public()
        scope = self.get_scope()

        if scope is None:
            return qs

        return qs.descendant_of(scope)

    def get_search_query(self):
        return self.request.GET.get("query", None)

    def get_scope(self):
        scope_id = safe_to_int(self.request.GET.get("scope"))

        if scope_id is None:
            return

        return Page.objects.filter(pk=scope_id).first()

    def do_search(self):
        qs = self.get_queryset()
        search_query = self.get_search_query()

        type = self.request.GET.get("type", None)
        if type is not None and type in self.page_types.keys():
            qs = qs.type(self.page_types[type])
        else:
            qs = qs.type(tuple(self.page_types.values()))

        for filter in self.current_filters(self.request):
            if filter["current_value"] is not None and len(filter["current_value"]) > 0:
                qs = filter["query"](qs, filter["current_value"])

        if search_query is not None:
            query = Query.get(search_query)
            query.add_hit()

            return qs.search(search_query)

        else:
            return qs

    def get_search_highlight(self, page):
        if hasattr(page, self.search_highlight_field):
            highlighter = SearchHeadline(
                self.search_highlight_field,
                query=SearchQuery(self.get_search_query()),
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

    def get_context_data(self, **kwargs):
        scope = self.get_scope()
        # search_results = list({p.localized for p in self.do_search()})
        search_results = self.do_search()
        paginator = Paginator(search_results, self.per_page)
        current_page_number = max(
            1, min(paginator.num_pages, safe_to_int(self.request.GET.get("page"), 1))
        )
        paginator_page = paginator.page(current_page_number)

        kwargs.update(
            {
                "scope": scope,
                "search_query": self.get_search_query(),
                "search_results": lambda: [
                    {
                        "page": page,
                        "search_highlight": lambda: self.get_search_highlight(
                            page.specific
                        ),
                    }
                    for page in paginator_page
                ],
                "pages": lambda: [page.specific for page in paginator_page],
                "total_count": paginator.count,
                "paginator_page": paginator_page,
                "paginator": paginator,
                "page_types": self.page_types.keys(),
                "request": self.request,
                "filters": self.current_filters(self.request),
            }
        )

        return super().get_context_data(**kwargs)

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

    # qs, url_value, UI label
    DEFAULT_ORDER_BY = "-date"
    order_by = {
        "alphabetical": {"query": ("title",), "label": "Sort alphabetically (A to Z)"},
        "-alphabetical": {
            "query": ("-title",),
            "label": "Sort reverse alphabetically (Z to A)",
        },
        DEFAULT_ORDER_BY: {
            "query": ("-first_published_at",),
            "label": "Sort most recent",
        },
        "date": {"query": ("first_published_at",), "label": "Sort oldest first"},
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

    def current_order_by_key(self):
        order_by = self.request.GET.get("order_by", self.DEFAULT_ORDER_BY)
        if order_by is None or order_by not in self.order_by.keys():
            order_by = self.DEFAULT_ORDER_BY
        return order_by

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

            qs = qs.search(search_query)

        order_by = self.order_by[self.current_order_by_key()]["query"]
        qs = qs.order_by(*order_by)

        return qs

    def get_context_data(self, **kwargs):
        scope = self.get_scope()
        search_results = self.do_search()
        paginator = Paginator(search_results, self.per_page)
        current_page_number = max(1, int(self.request.GET.get("page", 1)))
        paginator_page = paginator.page(current_page_number)

        kwargs.update(
            {
                "scope": scope,
                "search_query": self.get_search_query(),
                "pages": lambda: list(
                    {page.localized.specific for page in paginator_page}
                ),
                "paginator_page": paginator_page,
                "paginator": paginator,
                "page_types": self.page_types.keys(),
                "request": self.request,
                "filters": self.current_filters(self.request),
                "order_by": self.order_by,
                "current_order_by_key": self.current_order_by_key(),
            }
        )

        return super().get_context_data(**kwargs)

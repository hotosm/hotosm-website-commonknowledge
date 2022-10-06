from math import ceil

from django.contrib.postgres.search import SearchHeadline, SearchQuery
from django.core.paginator import Paginator
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from wagtail.core.models import Page
from wagtail.search.models import Query

from app.helpers import concat_html, safe_to_int


class SearchableDirectoryMixin(Page):
    search_highlight_field = "content"
    per_page = 9

    class Meta:
        abstract = True

    def get_search_query(self, request):
        return request.GET.get("query")

    def do_search(self, request):
        search_query = self.get_search_query(request)

        if search_query:
            query = Query.get(search_query)
            query.add_hit()

            return self.get_children().live().public().search(search_query)
        else:
            return self.get_children().live().public()

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

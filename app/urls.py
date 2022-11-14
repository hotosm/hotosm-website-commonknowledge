import debug_toolbar
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path
from django.views.generic.base import TemplateView
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.contrib.sitemaps.views import sitemap
from wagtail.documents import urls as wagtaildocs_urls
from wagtailautocomplete.urls.admin import urlpatterns as autocomplete_admin_urls

from app.views.search import SearchView

urlpatterns = [
    path("admin/autocomplete/", include(autocomplete_admin_urls)),
    path("django-admin/", admin.site.urls),
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("sitemap.xml", sitemap),
    path(
        "robots.txt",
        TemplateView.as_view(template_name="app/robots.txt", content_type="text/plain"),
    ),
]

urlpatterns += i18n_patterns(
    path("search/", SearchView.as_view(), name="search"),
    path(
        "frames/search/",
        SearchView.as_view(template_name="app/frames/search.html"),
        name="search_frame",
    ),
    path("", include(wagtail_urls)),
)

if settings.DEBUG:
    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG_TOOLBAR_ENABLED:
    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
    ]

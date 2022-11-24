from wagtail.api.v2.router import WagtailAPIRouter
from wagtail.api.v2.views import PagesAPIViewSet
from wagtail.documents.api.v2.views import DocumentsAPIViewSet
from wagtail.images.api.v2.views import ImagesAPIViewSet

# Create the router. "wagtailapi" is the URL namespace
wagtail_api_router = WagtailAPIRouter("wagtailapi")

# Add the three endpoints using the "register_endpoint" method.
# The first parameter is the name of the endpoint (eg. pages, images). This
# is used in the URL of the endpoint
# The second parameter is the endpoint class that handles the requests
wagtail_api_router.register_endpoint("pages", PagesAPIViewSet)
wagtail_api_router.register_endpoint("images", ImagesAPIViewSet)
wagtail_api_router.register_endpoint("documents", DocumentsAPIViewSet)


def preprocessing_hooks(endpoints):
    # your modifications to the list of operations that are exposed in the schema
    new_endpoints = []
    for (path, path_regex, method, callback) in endpoints:
        # If path starts with /api/v2 then add it to new_endpoints
        if path.startswith("/api/v2"):
            new_endpoints.append((path, path_regex, method, callback))
    return new_endpoints

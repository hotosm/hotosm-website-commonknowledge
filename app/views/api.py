from django.urls import path
from drf_spectacular.utils import extend_schema
from rest_framework import serializers, viewsets
from rest_framework.response import Response
from wagtail.api.v2.utils import BadRequestError
from wagtail.core.models import Page

from app.models import EventPage, OrganisationPage, PersonPage, ProjectPage
from app.serializers import PageCoordinatesSerializer
from app.utils.wagtail import localized_pages


class MapSearchViewset(viewsets.ReadOnlyModelViewSet):
    """
    Query the page metadata index, filtering by tag, returning a geojson FeatureCollection
    """

    page_types = (
        ProjectPage,
        OrganisationPage,
        PersonPage,
        EventPage,
    )

    class RequestSerializer(serializers.Serializer):
        pass

    model = Page
    serializer_class = PageCoordinatesSerializer

    def get_queryset(self):
        params = MapSearchViewset.RequestSerializer(data=self.request.GET)
        if not params.is_valid():
            raise BadRequestError()

        # If no filters, return all possible geo pages
        return Page.objects.live().specific().type(*self.page_types)

    @extend_schema(parameters=[RequestSerializer])
    def list(self, request):
        pages = localized_pages(self.get_queryset())
        return Response(PageCoordinatesSerializer(pages, many=True).data)

    def get_object(self, request):
        page = self.get_queryset()
        return Response(PageCoordinatesSerializer(page.localized).data)

    @classmethod
    def get_urlpatterns(cls):
        return [
            path("", cls.as_view({"get": "list"}), name="geo.search"),
        ]

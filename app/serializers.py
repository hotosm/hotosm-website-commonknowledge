from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_gis.serializers import (
    GeoFeatureModelSerializer,
    GeometrySerializerMethodField,
)

from app.models.wagtail import ProjectPage


class UserSerializer(serializers.Serializer):
    class Meta:
        model = get_user_model()
        fields = [
            "username",
            "id",
        ]


class PageCoordinatesSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = ProjectPage
        geo_field = "centroid"
        id_field = "id"
        fields = (
            "id",
            "label",
            "title",
            "geographical_location",
            "related_countries",
            "coordinates",
            "url",
            "map_image_url",
            "has_unique_location",
        )

    centroid = GeometrySerializerMethodField()

    def get_centroid(self, state):
        return state.centroid

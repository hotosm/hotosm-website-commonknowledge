from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer


class UserSerializer(serializers.Serializer):
    class Meta:
        model = User
        fields = [
            "username",
            "id",
        ]


class PageCoordinatesSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = "app.GeocodedMixin"
        geo_field = "centroid"
        fields = "__all__"

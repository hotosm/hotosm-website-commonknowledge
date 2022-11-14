from django.contrib.gis.geos import GEOSGeometry, Point
from django.test import TestCase

from app.models.wagtail import CountryPage


class DummyTestCase(TestCase):
    def test_countries_are_acceptable_to_stripe(self):
        self.assertEqual(True, True)


class TestCountryPageCase(TestCase):
    def setUp(self):
        self.country = CountryPage(title="United Kingdom", isoa2="GB", isoa3="GBR")

    def test_coordinates_for_country(self):
        self.assertIsInstance(self.country.centroid, Point)

    def test_geometry_for_country(self):
        self.assertIsInstance(self.country.geometry, GEOSGeometry)

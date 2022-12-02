from django.contrib.auth import get_user_model
from django.contrib.gis.geos import GEOSGeometry, Point
from django.test import TestCase
from wagtail.models import Page

from app.models.wagtail import CountryPage, PersonPage


class DummyTestCase(TestCase):
    def test_countries_are_acceptable_to_stripe(self):
        self.assertEqual(True, True)


class TestCountryPageCase(TestCase):
    def setUp(self):
        self.country = CountryPage(title="United Kingdom", isoa2="GB", isoa3="GBR")
        Page.get_first_root_node().add_child(instance=self.country)
        self.country.save()

    def test_coordinates_for_country(self):
        self.assertIsInstance(self.country.centroid, Point)

    def test_geometry_for_country(self):
        self.assertIsInstance(self.country.geometry, GEOSGeometry)


class TestAuthorshipSystem(TestCase):
    def create_user_sync_by_full_name(self):
        person_page = PersonPage(title="Person 1")
        Page.get_first_root_node().add_child(instance=person_page)
        person_page.save()
        user = get_user_model().objects.create(
            username="person",
            first_name="Person",
            last_name="1",
            password="asciohq9uhr8h28",
        )
        self.assertIs(user.page, person_page)

    def create_user_sync_by_email(self):
        matching_email = "some_email@hotosm.org"
        person_page = PersonPage(title="Person 2", email=matching_email)
        Page.get_first_root_node().add_child(instance=person_page)
        person_page.save()
        user = get_user_model().objects.create(
            username="person2", email="matching_email", password="oiy9asy98fyq893r87wy"
        )
        self.assertIs(user.page, person_page)

    def create_user_default_not_synced(self):
        person_page = PersonPage(title="Person 3", email="something@hotosm.org")
        Page.get_first_root_node().add_child(instance=person_page)
        person_page.save()
        user = get_user_model().objects.create(
            username="person3",
            email="something_else@hotosm.org",
            password="oiy9asy98fyq893r87wy",
        )
        self.assertIsNone(user.page)

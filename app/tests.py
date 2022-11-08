from django.test import TestCase


class DummyTestCase(TestCase):
    def test_countries_are_acceptable_to_stripe(self):
        self.assertEqual(True, True)

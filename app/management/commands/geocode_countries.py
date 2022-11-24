import time

from django.core.management.base import BaseCommand
from django.db import transaction

from app.models import CountryPage


class GeocodeCountriesCommand(BaseCommand):
    help = "Sync all CountryPage coordinates so that pages can be geo-tagged via related_countries."

    def handle(self, *args, **options):
        centroids = CountryPage.get_centroids()
        for country in CountryPage.objects.all():
            if country.centroid is None:
                country.save_centroid(centroids)

import time

from django.core.management.base import BaseCommand
from django.db import transaction

from app.models import CountryPage


class Command(BaseCommand):
    """
    main thing of interest is the WagtailHtmlRenderer class,
    which renders markdown as wagtail-friendly html using its custom notation for links.

    Other key thing is to create all the pages and images before setting their content
    so that the referenced pages all exist when the html gets rendered out
    """

    help = "Set up essential pages"

    def handle(self, *args, **options):
        centroids = CountryPage.get_centroids()
        for country in CountryPage.objects.all():
            if country.centroid is None:
                country.save_centroid(centroids)

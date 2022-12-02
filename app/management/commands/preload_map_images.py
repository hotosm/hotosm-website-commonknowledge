import json

import pycountry
from django.core.management.base import BaseCommand
from django.db import transaction

from app.models import CountryPage
from app.utils.python import ensure_1D_list
from app.views.api import MapSearchViewset


class Command(BaseCommand):
    help = "Preload map imagery to help make the map load faster"

    @transaction.atomic
    def handle(self, *args, **options):
        for page_type in MapSearchViewset.page_types:
            for page in page_type.objects.all():
                print("Rendered", page.map_image_url)

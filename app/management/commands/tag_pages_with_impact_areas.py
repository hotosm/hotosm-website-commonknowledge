import json
import re

import pycountry
from django.core.management.base import BaseCommand
from django.db import transaction
from wagtail.core.models import Locale

from app.models import ImpactAreaPage, ProjectPage
from app.utils.python import ensure_1D_list


class Command(BaseCommand):
    help = "Update `related_impact_areas` fields for project pages, using data from their `frontmatter` field if migrated from the old site."

    def add_arguments(self, parser):
        parser.add_argument("--locale", dest="locale", type=str, default="en")

    @transaction.atomic
    def handle(self, *args, **options):
        self.locale = Locale.objects.get(language_code=options.get("en", "en"))
        self.map = self.get_map()
        self.loop_pages((ProjectPage,), "Impact Area")

    def update_page(self, page, found_pages):
        page.related_impact_areas.add(*found_pages)
        revision = page.save_revision()
        if page.live:
            page.publish(revision)

    def try_adding_to_found_pages(self, listed_item, found_pages):
        listed_item = re.sub(r"/\s+/", " ", listed_item)
        page = self.map.get(listed_item, None)
        if page is not None:
            found_pages.append(page)
        return found_pages

    def get_map(self):
        return {
            """
            Accessible healthcare infrastructure and informed public health programming and monitoring.
            """
            "Public Health": ImpactAreaPage.objects.filter(title__icontains="Health")
            .first()
            .get_translation(self.locale),
            #
            """
            Preparedness, anticipatory action, risk reduction; and responding to the impacts of rapid onset and prolonged natural disasters.
            """
            "Disaster Risk Reduction": ImpactAreaPage.objects.filter(
                title__icontains="Disaster"
            )
            .first()
            .get_translation(self.locale),
            "Disasters & Climate Resilience": ImpactAreaPage.objects.filter(
                title__icontains="Disaster"
            )
            .first()
            .get_translation(self.locale),
            "Disaster Response": ImpactAreaPage.objects.filter(
                title__icontains="Disaster"
            )
            .first()
            .get_translation(self.locale),
            #
            """
            Service delivery and infrastructure in disadvantaged urban and rural areas, including transportation, water and sanitation, and energy.
            """
            "Sustainable Cities & Communities": ImpactAreaPage.objects.filter(
                title__icontains="Cities"
            )
            .first()
            .get_translation(self.locale),
            "Sustainable Cities": ImpactAreaPage.objects.filter(
                title__icontains="Cities"
            )
            .first()
            .get_translation(self.locale),
            "Transportation": ImpactAreaPage.objects.filter(title__icontains="Cities")
            .first()
            .get_translation(self.locale),
            "Water & Sanitation": ImpactAreaPage.objects.filter(
                title__icontains="Cities"
            )
            .first()
            .get_translation(self.locale),
            "Poverty Elimination": ImpactAreaPage.objects.filter(
                title__icontains="Cities"
            )
            .first()
            .get_translation(self.locale),
            "Clean Energy": ImpactAreaPage.objects.filter(title__icontains="Cities")
            .first()
            .get_translation(self.locale),
            "Technology Development": ImpactAreaPage.objects.filter(
                title__icontains="Cities"
            )
            .first()
            .get_translation(self.locale),
            "Environment": ImpactAreaPage.objects.filter(title__icontains="Cities")
            .first()
            .get_translation(self.locale),
            #
            """
            Improved understanding and accounting of gendered experiences & issues in all impact areas.
            """
            "Gender Equality": ImpactAreaPage.objects.filter(title__icontains="Gender")
            .first()
            .get_translation(self.locale),
            #
            """
            Coordinated service delivery for migrants and people displaced from home in transit, camp settings, and other informal contexts.
            """
            "Displacement & Safe Migration": ImpactAreaPage.objects.filter(
                title__icontains="Displacement"
            )
            .first()
            .get_translation(self.locale),
            "Refugee Response": ImpactAreaPage.objects.filter(
                title__icontains="Displacement"
            )
            .first()
            .get_translation(self.locale),
        }

    def loop_pages(self, page_types, frontmatter_key):
        """
        Generic loop for working with frontmatter key of page types.
        Override the class methods for specific implementations.
        """
        for page_type in page_types:
            for page in page_type.objects.all():
                if hasattr(page, "frontmatter") and page.frontmatter is not None:
                    frontmatter = page.frontmatter
                    if isinstance(page.frontmatter, str):
                        frontmatter = json.loads(page.frontmatter)
                    listed_in_frontmatter = ensure_1D_list(
                        frontmatter.get(frontmatter_key, list())
                    )
                    if len(listed_in_frontmatter) > 0:
                        found_pages = []
                        for listed_item in listed_in_frontmatter:
                            if (
                                listed_item is not None
                                and isinstance(listed_item, str)
                                and len(listed_item) > 0
                            ):
                                try:
                                    found_pages = self.try_adding_to_found_pages(
                                        listed_item, found_pages
                                    )
                                except LookupError:
                                    pass
                        if len(found_pages) > 0:
                            self.update_page(page, found_pages)
                        found_pages = []

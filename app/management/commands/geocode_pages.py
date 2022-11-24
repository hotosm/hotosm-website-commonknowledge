import json

import pycountry
from django.core.management.base import BaseCommand
from django.db import transaction

from app.models import CountryPage
from app.utils.python import ensure_1D_list
from app.views.api import MapSearchViewset


class Command(BaseCommand):
    help = "Update `related_countries` fields for all pages, using data from their `frontmatter` field if migrated from the old site."

    @transaction.atomic
    def handle(self, *args, **options):
        country_code_database_map = {
            country.isoa2: country for country in CountryPage.objects.all()
        }
        country_root_page = CountryPage.objects.first().get_parent()
        for page_type in MapSearchViewset.page_types:
            for page in page_type.objects.all():
                if hasattr(page, "frontmatter") and page.frontmatter is not None:
                    frontmatter = page.frontmatter
                    if isinstance(page.frontmatter, str):
                        frontmatter = json.loads(page.frontmatter)
                    listed_countries = ensure_1D_list(
                        frontmatter.get("Country", list())
                    )
                    if len(listed_countries) > 0:
                        country_pages = []
                        for listed_country in listed_countries:
                            if (
                                listed_country is None
                                or not isinstance(listed_country, str)
                                or len(listed_country) == 0
                            ):
                                try:
                                    results = pycountry.countries.search_fuzzy(
                                        listed_country
                                    )
                                    if len(results) != 0:
                                        metadata = results[0]
                                        country_instance = (
                                            country_code_database_map.get(
                                                metadata.alpha_2, None
                                            )
                                        )
                                        if country_instance is None:
                                            country_instance = (
                                                CountryPage.create_for_code(
                                                    metadata.alpha_2
                                                )
                                            )
                                            country_root_page.add_child(
                                                instance=country_instance
                                            )
                                            country_code_database_map[
                                                metadata.alpha_2
                                            ] = country_instance
                                        if country_instance is not None:
                                            country_pages.append(country_instance)
                                except LookupError:
                                    pass
                        if len(country_pages) > 0:
                            page.related_countries.add(*country_pages)
                            revision = page.save_revision()
                            if page.live:
                                page.publish(revision)
                        country_pages = []

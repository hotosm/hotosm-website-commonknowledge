import json

import pycountry
from django.core.management.base import BaseCommand
from django.db import transaction

from app.models import CountryPage
from app.utils.python import ensure_list
from app.views.api import MapSearchViewset


class Command(BaseCommand):
    """
    main thing of interest is the WagtailHtmlRenderer class,
    which renders markdown as wagtail-friendly html using its custom notation for links.

    Other key thing is to create all the pages and images before setting their content
    so that the referenced pages all exist when the html gets rendered out
    """

    help = "Set up essential pages"

    @transaction.atomic
    def handle(self, *args, **options):
        country_code_database_map = {
            country.isoa2: country for country in CountryPage.objects.all()
        }
        country_root_page = CountryPage.objects.first().get_parent()
        for page_type in MapSearchViewset.page_types:
            for page in page_type.objects.all():
                if page.frontmatter is not None:
                    frontmatter = page.frontmatter
                    if isinstance(page.frontmatter, str):
                        frontmatter = json.loads(page.frontmatter)
                    listed_countries = ensure_list(frontmatter.get("Country", list()))
                    print(page, type(listed_countries), listed_countries)
                    country_pages = []
                    for listed_country in listed_countries:
                        try:
                            results = pycountry.countries.search_fuzzy(listed_country)
                            if len(results) != 0:
                                metadata = results[0]
                                country_instance = country_code_database_map.get(
                                    metadata.alpha_2, None
                                )
                                if country_instance is None:
                                    country_instance = CountryPage.create_for_code(
                                        metadata.alpha_2
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

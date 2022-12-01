import json
import re

from django.core.management.base import BaseCommand
from django.db import transaction
from wagtail.core.models import Locale

from app.utils.python import ensure_1D_list


class BaseFrontmatterConverterCommand(BaseCommand):
    help = "Update `related_impact_areas` fields for project pages, using data from their `frontmatter` field if migrated from the old site."

    def add_arguments(self, parser):
        parser.add_argument("--locale", dest="locale", type=str, default="en")

    page_types = ()
    frontmatter_key = ""
    destination_field = ""

    @transaction.atomic
    def handle(self, *args, **options):
        self.locale = Locale.objects.get(language_code=options.get("en", "en"))
        self.loop_pages(self.page_types, self.frontmatter_key)

    def update_page(self, page, found_values):
        if (
            found_values is not None
            and self.destination_field is not None
            and hasattr(page, self.destination_field)
        ):
            old_value = getattr(page, self.destination_field)
            if old_value != found_values:
                setattr(page, self.destination_field, found_values)
                revision = page.save_revision()
                if page.live:
                    page.publish(revision)

    def try_adding_to_found_values(self, listed_item, found_values):
        return listed_item

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
                    raw_value = frontmatter.get(frontmatter_key, None)
                    if raw_value is not None:
                        if isinstance(raw_value, dict):
                            found_values = self.try_adding_to_found_values(
                                raw_value, list()
                            )
                            self.update_page(page, found_values)
                        elif isinstance(
                            raw_value,
                            (
                                str,
                                list,
                                tuple,
                            ),
                        ):
                            raw_value = ensure_1D_list(
                                frontmatter.get(frontmatter_key, list())
                            )
                            if len(raw_value) > 0:
                                found_values = []
                                for listed_item in raw_value:
                                    if (
                                        listed_item is not None
                                        and isinstance(listed_item, str)
                                        and len(listed_item) > 0
                                    ):
                                        try:
                                            found_values = (
                                                self.try_adding_to_found_values(
                                                    listed_item.lstrip().rstrip(),
                                                    found_values,
                                                )
                                            )
                                        except LookupError:
                                            pass
                                if len(found_values) > 0:
                                    self.update_page(page, found_values)
                                found_values = []
                        else:
                            raise ValueError(
                                "Frontmatter data couldn't be parsed for page",
                                type(page),
                                page,
                                type(raw_value),
                                raw_value,
                            )

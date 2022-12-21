from typing import List, TypedDict

import json

import pandas as pd
from django.core.management.base import BaseCommand
from django.http import HttpResponse
from wagtail.models import Page


class MigrationMappingRow(TypedDict):
    old_filepath: str
    old_url: str
    new_url: str
    page_type: str


class Command(BaseCommand):
    """
    Generate a CSV report for the content team
    """

    def add_arguments(self, parser):
        pass

    # @transaction.atomic
    def handle(self, *args, **options):
        print(generate_migration_report())


def generate_migration_report_view(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="migrationreport.csv"'},
    )
    csv = generate_migration_report()
    response.write(csv)
    return response


def generate_migration_report() -> str:
    data: List[MigrationMappingRow] = []
    for page in Page.objects.public().all():
        row = {
            "old_filepath": None,
            "old_url": None,
            "new_url": None,
            "page_type": None,
        }

        if (
            hasattr(page.specific, "frontmatter")
            and page.specific.frontmatter is not None
        ):
            frontmatter = page.specific.frontmatter

            # We saved this as char field instead of json field so need to convert
            if isinstance(frontmatter, str):
                frontmatter = json.loads(frontmatter)

            row.update(
                {
                    "old_filepath": frontmatter.get("path", ""),
                    "old_url": frontmatter.get("old_path", ""),
                }
            )

        row.update({"new_url": page.url, "page_type": page.specific_class.__name__})

        data.append(row)

    df = pd.DataFrame(data)
    return df.to_csv()

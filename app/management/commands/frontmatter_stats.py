import json
import pprint
import re
from datetime import date, datetime, time
from multiprocessing.sharedctypes import Value
from pathlib import Path
from statistics import mean
from urllib.parse import urlparse

import marko
import yaml
from bs4 import BeautifulSoup
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core import management
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify
from marko import block, inline
from marko.html_renderer import HTMLRenderer
from PIL import Image as PImage
from wagtail.core.rich_text import RichText
from wagtail.images.models import Image
from wagtail.models import Page, Site

from app.models.wagtail.pages import (
    ActivationIndexPage,
    ActivationProjectPage,
    ArticlePage,
    DirectoryPage,
    HomePage,
    MagazineIndexPage,
    MagazineSection,
    OpportunityPage,
    OrganisationPage,
    PersonPage,
    ProjectPage,
    StaticPage,
)


class Command(BaseCommand):
    """
    main thing of interest is the WagtailHtmlRenderer class,
    which renders markdown as wagtail-friendly html using its custom notation for links.

    Other key thing is to create all the pages and images before setting their content
    so that the referenced pages all exist when the html gets rendered out
    """

    help = "Set up essential pages"

    def add_arguments(self, parser):
        parser.add_argument("--source", dest="source", type=str)

        parser.add_argument(
            "--glob", action="append", default=[], dest="glob", type=str
        )

    @transaction.atomic
    def handle(self, *args, **options):
        print(options["source"])
        for glob in options["glob"]:
            frontmatter_stats = {}
            for path in Path(options["source"]).glob(glob):
                if path.suffix in {".md", ".markdown", ".mdx"}:
                    # print("Evaluating", path)
                    md, frontmatter = read_md(path)
                    for key, value in frontmatter.items():
                        if frontmatter_stats.get(key, None) is not None:
                            frontmatter_stats[key]["count"] += 1
                            if isinstance(value, list):
                                for v in value:
                                    if (
                                        frontmatter_stats[key]["values"].get(
                                            str(v), None
                                        )
                                        is not None
                                    ):
                                        frontmatter_stats[key]["values"][str(v)] += 1
                                    else:
                                        frontmatter_stats[key]["values"][str(v)] = 1
                            else:
                                if (
                                    frontmatter_stats[key]["values"].get(
                                        str(value), None
                                    )
                                    is not None
                                ):
                                    frontmatter_stats[key]["values"][str(value)] += 1
                                else:
                                    frontmatter_stats[key]["values"][str(value)] = 1
                        else:
                            frontmatter_stats[key] = {"count": 1, "values": {}}
                            if isinstance(value, list):
                                for v in value:
                                    frontmatter_stats[key]["values"][str(v)] = 1
                            else:
                                frontmatter_stats[key]["values"][str(value)] = 1
            sorted_keys = dict(
                sorted(
                    frontmatter_stats.items(), key=lambda x: x[1]["count"], reverse=True
                )
            )
            # pp = pprint.PrettyPrinter(indent=4, sort_dicts=False)
            # pp.pprint(sorted_keys)
            print("### `", Path(options["source"]) / glob, "`")
            print("<table>")
            print(
                "<thead><tr><th>Property</th><th>Count</th><th>Values</th></tr></thead>"
            )
            for property, stats in sorted_keys.items():
                print("<tr>")
                top_values = dict(
                    sorted(stats["values"].items(), key=lambda x: x[1], reverse=True)
                )
                if list(top_values.values())[0] > 1 and mean(top_values.values()) > 1.2:
                    popular_values_table = (
                        "<table><thead><tr><th>Value</th><th>Count</th></tr></thead>\n"
                    )
                    for value, count in list(top_values.items())[:8]:
                        popular_values_table += (
                            f"<tr><td>{value}</td><td>{count}</td>\n"
                        )
                    popular_values_table += "</table>"
                else:
                    popular_values_table = "Unique values only"
                print(
                    f"<tr><td>{property}</td><td>{stats['count']}</td><td>{popular_values_table}</td>"
                )
                print("</tr>")
            print("</table>")


def read_md(src):
    with open(src) as fd:
        data = fd.read()

    blocks = data.split("---")
    if len(blocks) < 3:
        return data, {}

    frontmatter = yaml.safe_load(blocks[1])
    md = marko.parse("---".join(blocks[2:]))

    return md, frontmatter

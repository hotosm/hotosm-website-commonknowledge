from typing import List, TypedDict

import json
import re
from datetime import date, datetime, time
from multiprocessing.sharedctypes import Value
from pathlib import Path
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
from django.db.utils import IntegrityError
from django.utils.text import slugify
from marko import block, inline
from marko.html_renderer import HTMLRenderer
from PIL import Image as PImage
from wagtail.contrib.redirects.models import Redirect
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


class PageData(TypedDict):
    frontmatter: dict
    content: str
    page: Page
    old_path: Path


class RedirectData(TypedDict):
    old_path: str
    redirect_to: Page


class Command(BaseCommand):
    """
    main thing of interest is the WagtailHtmlRenderer class,
    which renders markdown as wagtail-friendly html using its custom notation for links.

    Other key thing is to create all the pages and images before setting their content
    so that the referenced pages all exist when the html gets rendered out
    """

    help = "Set up essential pages"

    def add_arguments(self, parser):
        default_base_url = urlparse(settings.BASE_URL)

        parser.add_argument("--scratch", dest="scratch", type=bool, default=False)

        parser.add_argument("--source", dest="source", type=str)

        parser.add_argument("--dir", action="append", default=[], dest="dir", type=str)

        parser.add_argument(
            "-H", "--host", dest="host", type=str, default=default_base_url.hostname
        )
        parser.add_argument(
            "-p", "--port", dest="port", type=int, default=default_base_url.port or 80
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options.get("scratch"):
            Page.get_first_root_node().get_descendants().delete()
            Site.objects.all().delete()
            management.call_command("fixtree")

        # Define paths
        self.source_dir = Path(options["source"])
        self.path_mapping = dict()
        self.image_mapping = dict()

        # Setup root pages
        home, root, site = self.setup_root_pages(
            options.get("host"), options.get("port")
        )
        self.site = site
        self.home = home
        self.root = root
        self.unset_demo_pages()

        # Create pages
        ensure_child_page = self.ensure_child_page_factory(home)

        # magazine = ensure_child_page(
        #     MagazineIndexPage(slug="magazine", title="Magazine"))
        news = ensure_child_page(MagazineSection(slug="updates", title="Updates"))
        tech_blog = ensure_child_page(
            MagazineSection(slug="tech-blog", title="Tech Blog")
        )
        # news = ensure_child_page(MagazineSection(
        #     slug="tech-blog", title="Tech Blog"))
        people = ensure_child_page(DirectoryPage(slug="people", title="People"))
        opportunities = ensure_child_page(
            DirectoryPage(slug="opportunities", title="Opportunities")
        )
        partners = ensure_child_page(DirectoryPage(slug="partners", title="Partners"))
        projects = ensure_child_page(DirectoryPage(slug="projects", title="Projects"))
        working_groups = ensure_child_page(
            DirectoryPage(slug="working-groups", title="Working Groups")
        )
        rfps = ensure_child_page(DirectoryPage(slug="rfps", title="RFPs"))
        disaster_services_page = ensure_child_page(
            ActivationIndexPage(slug="disaster-services", title="Disaster Services")
        )

        content_map = {
            "*": {
                # "directories": ["_disaster_services"],
                "old_parent": "/",
                "page_type": StaticPage,
                "parent": home,
                "frontmatter_map": {
                    "Intro Text": "short_summary",
                },
            },
            "_disaster-services/*": {
                "old_parent": "/disaster-services/",
                # "directories": ["_disaster_services"],
                "page_type": ActivationProjectPage,
                "parent": disaster_services_page,
                "frontmatter_map": {
                    "Summary Text": "short_summary",
                    # TODO: Feature Image — file name
                },
            },
            "_partners/*": {
                "old_parent": "/partners/",
                # "directories": ["_partners"],
                "page_type": OrganisationPage,
                "parent": partners,
                "static_field_values": {"category": ["Partner"]},
            },
            "_people/*": {
                "old_parent": "/people/",
                "page_type": PersonPage,
                "parent": people,
                "frontmatter_map": {
                    # TODO: Photo — CDN url, sometimes absolute, sometimes relative
                    # TODO: Job Title / Team -> related "job" manytomanyfield
                },
            },
            "_people/staff/*": {
                "old_parent": "/people/",
                "page_type": PersonPage,
                "parent": people,
                "frontmatter_map": {
                    # TODO: Photo — CDN url, sometimes absolute, sometimes relative
                    # TODO: Job Title / Team -> related "job" manytomanyfield
                },
            },
            "_people/voting-members/*": {
                "old_parent": "/people/",
                "page_type": PersonPage,
                "parent": people,
                "frontmatter_map": {
                    # TODO: Photo — CDN url, sometimes absolute, sometimes relative
                    # TODO: Job Title / Team -> related "job" manytomanyfield
                },
            },
            "_people/archive/*": {
                "old_parent": "/people/",
                # "directories": ["_people/archive"],
                "page_type": PersonPage,
                "parent": people,
                "frontmatter_map": {
                    # TODO: Photo — CDN url, sometimes absolute, sometimes relative
                    # TODO: Job Title / Team -> related "job" manytomanyfield
                },
            },
            "_posts/*": {
                "old_parent": "/updates/",
                "page_type": ArticlePage,
                "parent": news,
                "frontmatter_map": {
                    # TODO: Feature Image — file name or URL
                    "Summary Text": "short_summary",
                    # TODO: Person[]
                    #       but this might not be a real person, so be careful!
                    # TODO: Perhaps also have a `byline` field?
                    # TODO: Working Group:
                    # TODO: Project:
                    # TODO: Sometimes this is not actually a relation
                    # TODO: Country:
                    # TODO: "Global"
                    # TODO: categories:
                    # TODO: tags:
                    # TODO: Tool
                },
            },
            "_press-releases/*": {
                "old_parent": "/press-releases/",
                "page_type": ArticlePage,
                "parent": news,
                "frontmatter_map": {
                    # TODO: Feature Image — file name or URL
                    "Summary Text": "short_summary",
                    # TODO: Person[]
                    #       but this might not be a real person, so be careful!
                    # TODO: Perhaps also have a `byline` field?
                    # TODO: Working Group:
                    # TODO: Project:
                    # TODO: Sometimes this is not actually a relation
                    # TODO: Country:
                    # TODO: "Global"
                    # TODO: categories:
                    # TODO: tags:
                    # TODO: Tool
                },
            },
            "_tech-blog/*": {
                "old_parent": "/tech-blog/",
                "page_type": ArticlePage,
                "parent": tech_blog,
                "frontmatter_map": {
                    # TODO: Feature Image — file name or URL
                    "Summary Text": "short_summary",
                    # TODO: Person[]
                    #       but this might not be a real person, so be careful!
                    # TODO: Perhaps also have a `byline` field?
                    # TODO: Working Group:
                    # TODO: Project:
                    # TODO: Sometimes this is not actually a relation
                    # TODO: Country:
                    # TODO: "Global"
                    # TODO: categories:
                    # TODO: tags:
                    # TODO: Tool
                },
            },
            "_projects/*": {
                "old_parent": "/projects/",
                "page_type": ProjectPage,
                "parent": projects,
                "frontmatter_map": {"Project Summary Text": "short_summary"},
            },
            "_volunteer-opportunities/*": {
                "old_parent": "/volunteer-opportunities/",
                "page_type": OpportunityPage,
                "parent": opportunities,
                "frontmatter_map": {
                    "Deadline Date": "deadline_datetime",
                    "Apply Form Link": "apply_form_url",
                },
            },
            "_rfps/*": {
                "page_type": OpportunityPage,
                "parent": rfps,
                "old_parent": "/rfps/",
                "frontmatter_map": {
                    "Deadline Date": "deadline_datetime",
                    "Apply Form Link": "apply_form_url",
                },
            },
            "_working-groups/*": {
                "old_parent": "/community/working-groups/",
                "page_type": OrganisationPage,
                # The community page was already created above
                "parent": working_groups,
                "frontmatter_map": {
                    "Summary Text": "short_summary",
                    # TODO:
                    # Coordination: https://trello.com/b/ZYzEoama/hot-training-wg
                    # Calendar: https://www.google.com/calendar/embed?src=hotosm.org_848e89aaiab04ag94d23rqn558%40group.calendar.google.com
                    # Chat: https://groups.google.com/a/hotosm.org/forum/#!forum/training
                    # Details: https://trello.com/c/XcJoZGbH/22-start-here
                    # Point of Contact: mailto:training@hotosm.org
                },
                "static_field_values": {"category": ["Working Group"]},
            },
        }

        pages: PageData = []
        redirects: List[RedirectData] = []

        print("=== Creating empty pages ===")
        for path, config in content_map.items():
            if len(options["dir"]) == 0 or path in options["dir"]:
                for path in self.source_dir.glob(path):
                    if path.suffix in {".md", ".markdown", ".mdx"}:
                        page = self.create_page(path, config)
                        if page:
                            pages.append(page)
                            redirects += self.accrue_redirects(page, path, config)

        print("=== Updating page content ===")
        for page_data in pages:
            print("Updating page content for", page_data["page"].url)
            self.set_page_content(page_data)

        # Redirects
        print("=== Creating redirects ===")
        self.create_redirects(redirects)

    def create_page(self, src: Path, config):
        content, frontmatter = read_md(src)

        if frontmatter.get("title", None) is None:
            return

        # Get page slug
        # Initially from filename
        old_slug = src.stem
        dated_slug_match = re.search("^([0-9]{4}-[0-9]{2}-[0-9]{2})-(.*)", old_slug)
        # There are some frontmatter things which override the slug / URL in general
        if "permalink" in frontmatter and (
            # Jekyll allowed slugs that included /, but this is off-limits to Wagtail
            frontmatter["permalink"]
            != "updates/2013-01-03_public/private_partnership_to_map_west_nusa_tenggara"
            and frontmatter["permalink"]
            != "updates/2013-11-11_remote_hot_activation_in_the_philippines_for_typhoon_yolanda/haiyan"
        ):
            permalink = Path(frontmatter["permalink"])
            old_slug = permalink.stem
        elif "urlname" in frontmatter:
            old_slug = frontmatter["urlname"]
        # Some articles have a date prefix, which is removed in the old system
        elif dated_slug_match:
            old_slug = dated_slug_match.group(2)
        # Slugify the title to be sure it can be ingested by Wagtail.
        # If there are any changes, a redirect will be created on comparison with the `old_path` (below)
        slug = slugify(old_slug)

        # Get original URL
        if "permalink" in frontmatter:
            old_path = Path(frontmatter["permalink"])
        else:
            # If there is no permalink, we can guess the URL based on the old site's structure and the slug
            if "old_parent" in config:
                old_parent_path = Path(config["old_parent"])
            else:
                old_parent_path = src.parent.relative_to(self.source_dir)
            old_path = old_parent_path / old_slug

        # Page fields

        # Standard fields
        args = {
            "title": frontmatter["title"],
            "slug": slug,
            "frontmatter": json.dumps(
                {**frontmatter, "old_path": str(old_path), "path": src}, cls=DTEncoder
            ),
            # "featured_image": image,
        }

        if "created" in frontmatter:
            args["first_published_at"] = to_date(frontmatter["created"])

        if "date" in frontmatter:
            args["last_published_at"] = to_date(frontmatter["date"])

        # Auto-mapped fields
        model_fields = config["page_type"]._meta.get_fields()
        for frontmatter_key, value in frontmatter.items():
            for field in model_fields:
                if frontmatter_key == field or to_snake_case(frontmatter_key) == field:
                    args[field] = value

        # Manually mapped fields
        for k, v in config.get("frontmatter_map", {}).items():
            if k in frontmatter:
                args[v] = frontmatter[k]

        # Create
        q = config["parent"].get_children().filter(slug=slug)
        if not q.exists():
            page = config["page_type"](**args)
            print(config["parent"], page)
            config["parent"].add_child(instance=page)
            page.save()
        else:
            page = q.get()

        if frontmatter.get("published", True) == False:
            page.unpublish()

        self.path_mapping[str(old_path)] = page

        return {
            "frontmatter": frontmatter,
            "content": content,
            "page": page,
            "old_path": old_path,
        }

    def set_page_content(
        self,
        page: PageData,
    ):
        content = page["content"]
        page = page["page"]

        if content is None:
            return
        renderer = WagtailHtmlRenderer(self.path_mapping, self.image_mapping, page.url)
        wagtail_html = renderer.render(content)
        if wagtail_html is not None and len(wagtail_html) > 0:
            page.content = json.dumps([{"type": "richtext", "value": wagtail_html}])
            page.save()

    def setup_root_pages(self, host: str, port: int):
        root = Page.get_first_root_node()
        try:
            site = Site.objects.get(
                root_page__content_type=ContentType.objects.get_for_model(HomePage)
            )
            home = site.root_page
            print("Site and homepage already set up", site, home)
        except:
            home = HomePage(
                title=settings.WAGTAIL_SITE_NAME,
                slug=slugify(settings.WAGTAIL_SITE_NAME),
            )
            root.add_child(instance=home)

            site, is_new = Site.objects.get_or_create(
                hostname=host,
                port=port,
                is_default_site=True,
                site_name=settings.WAGTAIL_SITE_NAME,
                root_page=home,
            )
        return home, root, site

    def unset_demo_pages(self):
        # Delete placeholders
        DEFAULT_WAGTAIL_PAGE_TITLE = "Welcome to your new Wagtail site!"
        Page.objects.filter(title=DEFAULT_WAGTAIL_PAGE_TITLE).all().unpublish()

    def ensure_child_page_factory(self, root_page: Page):
        def ensure_child_page(page_instance: Page, parent_page=root_page):
            existing = parent_page.get_children().filter(slug=page_instance.slug)
            if not existing.exists():
                parent_page.add_child(instance=page_instance)
            else:
                model = existing.first().specific_class
                if model != page_instance.specific_class:
                    raise ValueError(
                        f"Slug exists ({page_instance.slug}), but type {model} !== required type {page_instance.specific_class}. Manual intervention required."
                    )
                print("Already exists:", page_instance.specific_class, page_instance)
            return page_instance

        return ensure_child_page

    def accrue_redirects(self, page_data: PageData, path: Path, config: dict):
        redirects: List[RedirectData] = []

        # Leave a redirect if the page was moved, either by us or by permalink
        old = "/" + str(page_data["old_path"]).lstrip("/").rstrip("/")
        new = "/" + page_data["page"].url.lstrip("/en/").lstrip("/").rstrip("/")
        if old != new:
            print("⚠️ Redirect required:", old, new)
            redirects.append(
                {
                    "old_path": "/"
                    + str(page_data["old_path"]).lstrip("/").rstrip("/"),
                    "redirect_to": page_data["page"],
                }
            )

        # Leave redirects for the `redirect_from` property in frontmatter
        if "redirect_from" in page_data["frontmatter"]:
            redirect_from_list = (
                page_data["frontmatter"]["redirect_from"]
                if type(page_data["frontmatter"]["redirect_from"]) == list
                else [page_data["frontmatter"]["redirect_from"]]
            )
            for redirect_from in redirect_from_list:
                redirects.append(
                    {
                        "old_path": "/" + redirect_from.lstrip("/").rstrip("/"),
                        "redirect_to": page_data["page"],
                    }
                )

        return redirects

    def create_redirects(self, redirects: List[RedirectData]):
        for redirect in redirects:
            print("Creating redirect", redirect)
            try:
                Redirect.add_redirect(
                    redirect["old_path"], redirect["redirect_to"], site=self.site
                )
            except IntegrityError:
                pass


def to_date(x):
    if not x:
        return

    if isinstance(
        x,
        (
            date,
            datetime,
        ),
    ):
        return x
    elif isinstance(x, int):
        return datetime.fromtimestamp(x)
    else:
        return date.fromisoformat(x)


def read_md(src):
    with open(src) as fd:
        data = fd.read()

    blocks = data.split("---")
    if len(blocks) < 3:
        return data, {}

    frontmatter = yaml.safe_load(blocks[1])
    md = marko.parse("---".join(blocks[2:]))

    return md, frontmatter


class WagtailHtmlRenderer(HTMLRenderer):
    # TODO: Fix html issues with OLs
    # e.g. Malaria Elimination Mapping Continues

    def __init__(self, page_mapping: dict, image_mapping: dict, base: str):
        super().__init__()
        self.page_mapping = page_mapping
        self.image_mapping = image_mapping
        self.base = base

    def render(self, element):
        html = super().render(element)
        if html is not None and len(html) > 0:
            return BeautifulSoup(html, "html5lib").prettify()
        return html

    def render_heading(self, element):
        level = element.level + 1

        return "<h{level}>{children}</h{level}>\n".format(
            level=level, children=self.render_children(element)
        )

    def render_link(self, element: inline.Link):
        if element.dest.startswith("/"):
            href = element.dest.strip("/")
        else:
            href = self.base + "/" + element.dest.strip("/")

        page = self.page_mapping.get(href)
        if page is None:
            return super().render_link(element)

        template = '<a linktype="page" id="{}" {}>{}</a>'
        title = f' title="{self.escape_html(element.title)}"' if element.title else ""
        body = self.render_children(element)
        return template.format(page.id, title, body)

    # TODO:
    # def render_image(self, element: inline.Image):
    #     slug = Path(element.dest).relative_to("../../assets")
    #     image = self.image_mapping[str(slug)]

    #     template = '<embed embedtype="image" id="{}" alt="{}" format="left" />'
    #     title = f' title="{self.escape_html(element.title)}"' if element.title else ""
    #     render_func = self.render
    #     self.render = self.render_plain_text
    #     body = self.render_children(element)
    #     self.render = render_func
    #     return template.format(image.id, title or body)

    def render_plain_text(self, element):
        if hasattr(element, "children") and isinstance(element.children, str):
            return self.escape_html(element.children)
        return self.render_children(element)

    def render_blank_line(self, element):
        return ""

    def render_children(self, element):
        if not hasattr(element, "children"):
            return ""

        rendered = [self.render(child) for child in element.children]  # type: ignore
        return "".join(rendered)


def to_snake_case(name):
    name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    name = re.sub("__([A-Z])", r"_\1", name)
    name = re.sub("([a-z0-9])([A-Z])", r"\1_\2", name)
    return name.lower()


class DTEncoder(json.JSONEncoder):
    def default(self, obj):
        # 👇️ if passed in object is datetime object
        # convert it to a string
        if isinstance(obj, datetime):
            return str(obj)
        # 👇️ otherwise use the default behavior
        try:
            return json.JSONEncoder.default(self, obj)
        except:
            return str(obj)

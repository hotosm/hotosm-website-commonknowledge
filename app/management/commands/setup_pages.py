from urllib.parse import urlparse

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify
from wagtail.models import Page, Site

from app.models import HomePage, MagazineIndexPage
from app.models.wagtail.pages import StaticPage, TopicHomepage


class Command(BaseCommand):
    help = "Set up essential pages"

    def add_arguments(self, parser):
        default_base_url = urlparse(settings.BASE_URL)

        parser.add_argument(
            "-H", "--host", dest="host", type=str, default=default_base_url.hostname
        )
        parser.add_argument(
            "-p", "--port", dest="port", type=int, default=default_base_url.port or 80
        )

    @transaction.atomic
    def handle(self, *args, **options):
        home, root = self.setup_root_pages(options.get("host"), options.get("port"))
        self.unset_demo_pages()

        # Create pages
        ensure_child_page = self.ensure_child_page_factory(home)

        if settings.SETUP_DEMO_PAGES is not False:
            ensure_child_page(
                TopicHomepage(slug="start-mapping", title="Start Mapping")
            )
            ensure_child_page(
                TopicHomepage(slug="data-and-tools", title="Data & Tools")
            )
            ensure_child_page(TopicHomepage(slug="open-source", title="Open Source"))
            ensure_child_page(MagazineIndexPage(slug="news", title="News"))
            # TODO: Community
            # TODO: Partnerships
            ensure_child_page(StaticPage(slug="about", title="About"))

    def setup_root_pages(self, host: str, port: int):
        root = Page.get_first_root_node()
        try:
            site = Site.objects.get(
                root_page__content_type=ContentType.objects.get_for_model(HomePage)
            )
            home = site.root_page
            print("Site and homepage already set up", site, home)
        except:
            ensure_child_page = self.ensure_child_page_factory(root)
            home = ensure_child_page(
                HomePage(
                    title=settings.WAGTAIL_SITE_NAME,
                    slug=slugify(settings.WAGTAIL_SITE_NAME),
                )
            )

            site = Site.objects.get_or_create(
                hostname=host,
                port=port,
                is_default_site=True,
                site_name=settings.WAGTAIL_SITE_NAME,
                root_page=home,
            )
        return home, root

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

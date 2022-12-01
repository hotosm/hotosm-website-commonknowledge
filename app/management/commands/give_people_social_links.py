import os.path
import re
from urllib.parse import quote_plus, urlsplit, urlunsplit

from app.models import PersonPage

from ..base_frontmatter_converter_command import BaseFrontmatterConverterCommand


class Command(BaseFrontmatterConverterCommand):
    help = "Tag people with relevant social media URLs via legacy frontmatter"

    page_types = (PersonPage,)
    frontmatter_key = "Social Media (Full URL)"

    def get_map(self):
        return {
            "LinkedIn": "linkedin_url",
            "Website": "website",
            "OSM": "osm_username",
            "Twitter": "twitter_username",
            "Facebook": "facebook_url",
        }

    def try_adding_to_found_values(self, listed_item, found_values):
        found_values = {}
        for source_key in listed_item:
            source_value = listed_item[source_key]
            target_field_name = self.get_map().get(source_key, None)
            if (
                target_field_name is not None
                and source_value is not None
                and len(source_value) > 0
            ):
                if target_field_name == "facebook_url" and "/" not in source_value:
                    source_value = f"https://facebook.com/{quote_plus(source_value)}"
                if target_field_name == "linkedin_url" and "/" not in source_value:
                    source_value = f"https://linkedin.com/in/{quote_plus(source_value)}"
                if target_field_name in (
                    "website",
                    "linkedin_url",
                    "facebook_url",
                ):
                    # Reconstruct the URL as sometimes people forget bits of it.
                    url_parts = urlsplit(source_value, scheme="https")
                    # Enforce, as sometimes people put http:// (or otherwise break the URL with something else)
                    url_parts = url_parts._replace(scheme="https")
                    source_value = urlunsplit(url_parts)
                    source_value = re.sub(r"\/\/\/+", "//", source_value)
                elif target_field_name in ("twitter_username", "osm_username"):
                    # Twitter users sometimes put @ in their username. Not necessary.
                    source_value = re.sub("@", "", source_value)
                    # Some people set URLs, some set usernames. Try and extract username in case.
                    if "/" in source_value:
                        url_parts = urlsplit(source_value, scheme="https")
                        # Get the username part of the URL
                        source_value = os.path.split(url_parts.path)[1]
                if source_value is not None:
                    found_values[target_field_name] = source_value
        return found_values

    def update_page(self, page, found_values):
        try:
            if len(found_values.values()) > 0:
                for field in found_values:
                    setattr(page, field, found_values[field])
                revision = page.save_revision()
                if page.live:
                    page.publish(revision)
        except Exception as e:
            print(page, found_values)
            raise e

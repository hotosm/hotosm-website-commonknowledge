from app.models import PersonPage

from ..base_frontmatter_converter_command import BaseFrontmatterConverterCommand


class Command(BaseFrontmatterConverterCommand):
    help = "Tag people with relevant categories via legacy frontmatter"

    page_types = (PersonPage,)
    frontmatter_key = "Member Type"

    def get_map(self):
        return {
            "Is Staff": "Staff",
            "Is Media Contact": "Media Contact",
            "Is Voting Member": "Voting Member",
            "Is Board Member": "Board Member",
        }

    def try_adding_to_found_values(self, listed_item, found_values):
        for key in listed_item:
            if listed_item[key] == True:
                tag = self.get_map().get(key, None)
                if tag is not None:
                    found_values.append(tag)
        return found_values

    def update_page(self, page, found_values):
        if len(found_values) > 0:
            page.category.add(*found_values)
            revision = page.save_revision()
            if page.live:
                page.publish(revision)

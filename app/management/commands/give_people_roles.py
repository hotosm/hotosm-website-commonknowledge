from app.management.commands.base_frontmatter_converter_command import (
    BaseFrontmatterConverterCommand,
)
from app.models import PersonPage


class Command(BaseFrontmatterConverterCommand):
    help = "Copy the frontmatter for Job Title to the django field 'role' for people"

    page_types = (PersonPage,)
    frontmatter_key = "Job Title"
    destination_field = "role"

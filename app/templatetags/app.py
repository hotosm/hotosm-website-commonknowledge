from django import template
from wagtail.models import Page

register = template.Library()


@register.filter(name="times")
def times(number):
    return range(number)


def highlighted_in_table_of_content(page: Page, current_page: Page):
    current_page_lineage = current_page.get_ancestors(inclusive=True)
    if page.id == current_page.id:
        return True
    elif current_page_lineage.filter(id=page.id).exists():
        return True
    else:
        return False


@register.simple_tag()
def is_ancestor(page: Page, current_page):
    return highlighted_in_table_of_content(page, current_page)


@register.simple_tag()
def if_ancestor(
    page: Page,
    current_page,
    ancestor_class: str = " text-hotRed ",
    unrelated_class: str = "  ",
):
    if highlighted_in_table_of_content(page, current_page):
        return ancestor_class
    return unrelated_class

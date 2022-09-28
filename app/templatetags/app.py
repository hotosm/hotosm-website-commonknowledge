from urllib import parse

from django import template
from django.http.request import HttpRequest
from django.urls import translate_url as _translate_url
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
    ancestor_class: str = " text-red ",
    unrelated_class: str = "  ",
):
    if highlighted_in_table_of_content(page, current_page):
        return ancestor_class
    return unrelated_class


@register.simple_tag(takes_context=True)
def querystring(context, **kwargs):
    """
    Add query kwargs to URL.

    e.g. {% querystring annual=None as url %}
    """
    request: HttpRequest = context.get("request", None)
    if request is None:
        return

    params = request.GET.dict()
    for key, value in kwargs.items():
        if value is None:
            params.pop(key, None)
        else:
            params[key] = value

    return "?" + parse.urlencode(params)


@register.simple_tag(takes_context=True)
def translate_url(context, lang=None, *args, **kwargs):
    """
    Only works for named routes
    """
    path = context["request"].path
    translated = _translate_url(path, lang)
    return translated


@register.simple_tag()
def get_wagtail_locale_codes():
    from wagtail.core.models import Locale

    return list(locale.language_code for locale in Locale.objects.all())

from django.utils.html import format_html_join


def concat_html(*items):
    return format_html_join("", "{}", ((x,) for x in items))


def safe_to_int(x, default=None):
    try:
        return int(x)
    except:
        return default


class classproperty:
    def __init__(self, f):
        self.f = f

    def __get__(self, obj, owner):
        return self.f(owner)

from functools import reduce


def join_slash(a, b):
    return a.rstrip("/") + "/" + b.lstrip("/")


def urljoin(*args):
    return reduce(join_slash, args) if args else ""

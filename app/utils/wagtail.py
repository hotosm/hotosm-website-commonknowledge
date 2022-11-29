from django.apps import apps
from django.db.models import Q, Subquery
from wagtail.models import Page

from app.utils.python import ensure_1D_list


def localized_related_pages(page, property: str):
    """
    Collect foreign key references for each translation of a page.
    """
    translations = page.get_translations(inclusive=True).all()
    related_pages = []
    for translation in translations:
        related_pages += list(getattr(translation, property).all())
    return ensure_1D_list(related_pages)


def localized_pages(pages):
    return list({p.specific.localized for p in list(pages)})


def model_subclasses(mclass):
    """Retrieve all model subclasses for the provided class"""
    return [m for m in apps.get_models() if issubclass(m, mclass)]


def abstract_page_query_filter(mclass, filter_params, pk_attr="page_ptr"):
    """Create a filter query that will be applied to all children of the provided
                abstract model class. Returns None if a query filter cannot be created.

    Example: Retrieve all page models descended from AbstractSiteContent where feature is True:
    ```
    qs_features = Page.objects.filter(
        abstract_page_query_filter(AbstractSiteContent, { 'feature': 'True' }))
    ```

                @returns Query or None
    """
    if not mclass._meta.abstract:
        raise ValueError("Provided model class must be abstract")

    pclasses = model_subclasses(mclass)

    # Filter for pages which are marked as features
    if len(pclasses):

        qf = Q(
            pk__in=Subquery(pclasses[0].objects.filter(**filter_params).values(pk_attr))
        )
        for c in pclasses[1:]:
            qf |= Q(pk__in=Subquery(c.objects.filter(**filter_params).values(pk_attr)))

        return qf

    return None

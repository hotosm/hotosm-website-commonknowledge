from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q
from modelcluster.fields import ParentalKey


class User(AbstractUser):
    page = ParentalKey(
        "app.PersonPage",
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
        related_name="user",
        help_text="Public profile page. Select from existing profiles, or create a new Person Page and come back here to select it.",
    )

    is_public = models.BooleanField(
        default=True,
        blank=True,
        null=True,
        help_text="Setting this to false will hide the user's contributions from page author lists, and will not create a PersonPage either.",
    )

    def get_or_create_page(self):
        from app.models import PersonPage

        return PersonPage.get_or_create_for_user(self)

    def save(self, *args, **kwargs) -> None:
        super().save(*args, **kwargs)
        self.refresh_page_authorship()

    def refresh_page_authorship(self):
        from wagtail.models import Page, Revision

        pages_edited_by_user = Page.objects.filter(
            Q(
                id__in=Revision.objects.filter(
                    base_content_type=ContentType.objects.get_for_model(Page), user=self
                ).values_list("pk", flat=True)
            )
            | (Q(owner=self))
        )
        for page in pages_edited_by_user:
            print(page)
            page.specific.save()

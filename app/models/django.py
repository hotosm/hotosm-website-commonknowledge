from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q
from modelcluster.fields import ParentalKey


class User(AbstractUser):
    page = models.ForeignKey(
        "app.PersonPage",
        on_delete=models.SET_NULL,
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

    def save(self, *args, **kwargs) -> None:
        try:
            if self.page is None:
                self.connect_person_page_if_exists()
            # self.refresh_page_authorship()
        except Exception as e:
            print(self)
            print(e)
        return super().save(*args, **kwargs)

    def connect_person_page_if_exists(self):
        from app.models import PersonPage

        page = PersonPage.match_for_user(self)
        if self.page is None:
            self.page = page

    def refresh_page_authorship(self):
        try:
            from wagtail.models import Page, Revision

            pages_edited_by_user = Page.objects.filter(
                Q(
                    id__in=[
                        int(id)
                        for id in Revision.objects.filter(
                            base_content_type=ContentType.objects.get_for_model(Page),
                            user=self,
                        ).values_list("object_id", flat=True)
                    ]
                )
                | (Q(owner=self))
            )
            for page in pages_edited_by_user:
                if hasattr(page.specific, "refresh_authors"):
                    page.specific.refresh_authors()
        except Exception as e:
            print(self)
            print(e)
            pass

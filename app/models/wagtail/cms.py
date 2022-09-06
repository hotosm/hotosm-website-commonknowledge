from django.db import models
from wagtail.documents.models import AbstractDocument, Document
from wagtail.fields import RichTextField
from wagtail.images.models import AbstractImage, AbstractRendition


class CMSImage(AbstractImage):
    # Making blank / null explicit because you *really* need alt text
    alt_text = models.CharField(
        max_length=1024,
        blank=False,
        null=False,
        default="",
        help_text="Describe this image as literally as possible. If you can close your eyes, have someone read the alt text to you, and imagine a reasonably accurate version of the image, you're on the right track.",
    )

    attribution = RichTextField(
        blank=True,
        null=True,
        features=["italic", "link"],
        help_text="What is the source of this image? Name, year, origin, so on.",
    )

    admin_form_fields = (
        "title",
        "alt_text",
        "attribution",
        "file",
    )


class ImageRendition(AbstractRendition):
    image = models.ForeignKey(
        CMSImage, on_delete=models.CASCADE, related_name="renditions"
    )

    class Meta:
        unique_together = (("image", "filter_spec", "focal_point_key"),)


class CMSDocument(AbstractDocument):
    import_ref = models.CharField(max_length=1024, null=True, blank=True)
    admin_form_fields = Document.admin_form_fields

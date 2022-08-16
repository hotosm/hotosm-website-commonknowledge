from email.policy import default

from django.db import models
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.fields import RichTextField


@register_setting(icon="warning")
class SiteBannerSetting(BaseSiteSetting):
    banner_active = models.BooleanField(default=False)
    title = models.CharField(max_length=300)
    description = RichTextField(features=["bold", "italic", "link"])
    url = models.CharField(max_length=800)

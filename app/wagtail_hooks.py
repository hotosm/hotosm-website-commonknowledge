from django.templatetags.static import static
from django.utils.html import format_html
from wagtail import hooks
from wagtail.admin.views.account import BaseSettingsPanel
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register

from app.forms import CustomUserSettingsForm
from app.models import ArticlePage, EventPage, PersonPage, ProjectPage


@hooks.register("insert_global_admin_css")
def global_admin_css():
    return format_html('<link rel="stylesheet" href="{}">', static("wagtailadmin.css"))


@hooks.register("register_account_settings_panel")
class CustomSettingsPanel(BaseSettingsPanel):
    name = "public_page"
    title = "Public profile page"
    order = 50
    form_class = CustomUserSettingsForm
    form_object = "user"


class PersonPageAdmin(ModelAdmin):
    model = PersonPage
    menu_label = "People pages"  # ditch this to use verbose_name_plural from model
    menu_icon = "user"  # change as required
    list_display = (
        "title",
        "locale",
        "role",
        "email",
    )
    search_fields = ("title",)
    order = 500


modeladmin_register(PersonPageAdmin)


class ProjectPageAdmin(ModelAdmin):
    model = ProjectPage
    list_display = (
        "title",
        "locale",
    )
    search_fields = ("title",)
    order = 500


modeladmin_register(ProjectPageAdmin)


class ArticlePageAdmin(ModelAdmin):
    model = ArticlePage
    list_display = (
        "title",
        "locale",
        "first_published_at",
        "last_published_at",
    )
    search_fields = ("title",)
    order = 500


modeladmin_register(ArticlePageAdmin)


class EventPageAdmin(ModelAdmin):
    model = EventPage
    list_display = (
        "title",
        "locale",
        "start_datetime",
        "end_datetime",
    )
    search_fields = ("title",)
    order = 500


modeladmin_register(EventPageAdmin)

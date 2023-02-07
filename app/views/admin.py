from typing import Any, Mapping, Union

from wagtail.admin.ui.components import Component
from wagtail.admin.views.home import HomeView


class ConnectYourPublicProfilePage(Component):
    name = "connect_your_public_profile_page"
    template_name = "app/admin/connect_your_public_profile_page.html"
    order = 100
    _version = "1"

    def get_dismissible_id(self) -> str:
        return f"{self.name}_{self._version}"

    def get_context_data(self, parent_context: Mapping[str, Any]) -> Mapping[str, Any]:
        return {
            "dismissible_id": self.get_dismissible_id(),
            "version": self._version,
            "edit_account_url": "/admin/account/",
        }

    def is_shown(self, parent_context: Mapping[str, Any] = None) -> bool:
        user = parent_context["request"].user
        profile = getattr(user, "wagtail_userprofile", None)

        if hasattr(user, "page") and user.page is not None:
            return False

        if profile and profile.dismissibles.get(self.get_dismissible_id()):
            return False

        return True

    def render_html(self, parent_context: Mapping[str, Any] = None) -> str:
        if not self.is_shown(parent_context):
            return ""
        return super().render_html(parent_context)


class CustomAdminHomePageView(HomeView):
    def get_panels(self):
        panels = super().get_panels()
        # panels += [ConnectYourPublicProfilePage()]
        return panels

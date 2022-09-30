from django.apps import AppConfig as _AppConfig


class AppConfig(_AppConfig):
    name = "app"

    def ready(self):
        """
        Called when the app is ready.
        """
        from .models import monkey_patch_richtext

        monkey_patch_richtext()

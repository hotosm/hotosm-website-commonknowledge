from django.core.exceptions import ValidationError


def task_manager_project_url_validator(value):
    if "https://tasks.hotosm.org/projects/" not in value:
        raise ValidationError(
            _("%(value)s should look like https://tasks.hotosm.org/projects/..."),
            params={"value": value},
        )

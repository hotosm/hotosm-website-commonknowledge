from django.core.exceptions import ValidationError


def github_repo_validator(value):
    if "https://github.com/" not in value:
        raise ValidationError(
            _("%(value)s should look like https://github.com/.../..."),
            params={"value": value},
        )

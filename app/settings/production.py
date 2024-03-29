from urllib.parse import urlparse

from .base import *

DEBUG = False
SECRET_KEY = os.getenv("SECRET_KEY")
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")
CSRF_TRUSTED_ORIGINS = os.getenv("CSRF_TRUSTED_ORIGINS", BASE_URL).split(",")


MIDDLEWARE += [
    "redirect_to_non_www.middleware.RedirectToNonWww",
]


if os.getenv("AWS_S3_REGION_NAME"):
    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
    AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME")
    AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
    AWS_S3_ENDPOINT_URL = os.getenv("AWS_S3_ENDPOINT_URL")
    AWS_S3_ACCESS_KEY_ID = os.getenv("AWS_S3_ACCESS_KEY_ID")
    AWS_S3_SECRET_ACCESS_KEY = os.getenv("AWS_S3_SECRET_ACCESS_KEY")
    AWS_S3_CUSTOM_DOMAIN = os.getenv("AWS_S3_CUSTOM_DOMAIN")
    MEDIA_URL = os.getenv("MEDIA_URL")
else:
    MEDIA_ROOT = os.getenv(MEDIA_ROOT)
    MEDIA_URL = os.getenv("MEDIA_URL", "/media/")


if os.getenv("MAILJET_API_KEY"):
    # if you don't already have this in settings
    DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "noreply@hotosm.org")
    # ditto (default from-email for Django errors)
    SERVER_EMAIL = DEFAULT_FROM_EMAIL
    ANYMAIL = {
        "SEND_DEFAULTS": {"envelope_sender": DEFAULT_FROM_EMAIL},
        "MAILJET_API_KEY": os.getenv("MAILJET_API_KEY"),
        "MAILJET_SECRET_KEY": os.getenv("MAILJET_SECRET_KEY"),
    }
    EMAIL_BACKEND = "anymail.backends.mailjet.EmailBackend"
elif os.getenv("MAILGUN_API_URL"):
    ANYMAIL = {
        "MAILGUN_API_URL": os.getenv("MAILGUN_API_URL"),
        "MAILGUN_API_KEY": os.getenv("MAILGUN_API_KEY"),
        "MAILGUN_SENDER_DOMAIN": os.getenv("MAILGUN_SENDER_DOMAIN"),
    }
    EMAIL_BACKEND = "anymail.backends.mailgun.EmailBackend"
    DEFAULT_FROM_EMAIL = f"noreply@{ANYMAIL['MAILGUN_SENDER_DOMAIN']}"
    ANYMAIL["SEND_DEFAULTS"] = {"envelope_sender": DEFAULT_FROM_EMAIL}
    # ditto (default from-email for Django errors)
    SERVER_EMAIL = f"admin@{ANYMAIL['MAILGUN_SENDER_DOMAIN']}"

WAGTAILTRANSFER_SECRET_KEY = os.getenv("WAGTAILTRANSFER_SECRET_KEY")
WAGTAILTRANSFER_SOURCES = {}

if os.getenv("WAGTAILTRANSFER_SECRET_KEY_STAGING"):
    WAGTAILTRANSFER_SOURCES["staging"] = {
        "BASE_URL": "https://alpha.hotosm.org/wagtail-transfer/",
        "SECRET_KEY": os.getenv("WAGTAILTRANSFER_SECRET_KEY_STAGING"),
    }

if os.getenv("WAGTAILTRANSFER_SECRET_KEY_PRODUCTION"):
    WAGTAILTRANSFER_SOURCES["production"] = {
        "BASE_URL": "https://hotosm-production.fly.dev/wagtail-transfer/",
        "SECRET_KEY": os.getenv("WAGTAILTRANSFER_SECRET_KEY_PRODUCTION"),
    }


try:
    from .local import *
except ImportError:
    pass

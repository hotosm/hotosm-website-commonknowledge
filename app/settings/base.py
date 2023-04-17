import os
import re

import dj_database_url
import posthog
from django.conf.locale import LANG_INFO

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(PROJECT_DIR)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

DEBUG_TOOLBAR_ENABLED = False

# Application definition

INSTALLED_APPS = [
    "app",
    "anymail",
    "rest_framework",
    "rest_framework_gis",
    "drf_spectacular",
    "groundwork.core",
    "groundwork.geo",
    "livereload",
    "django_vite",
    "django.contrib.gis",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "wagtail.embeds",
    "wagtail.sites",
    "wagtail.users",
    "wagtail.snippets",
    "wagtail.documents",
    "wagtail.images",
    "wagtail.search",
    "wagtail_localize",
    "wagtail_localize.locales",  # This replaces "wagtail.locales"
    "wagtail.contrib.forms",
    "wagtail.contrib.redirects",
    "wagtail.admin",
    "wagtail",
    "wagtail.api.v2",
    "modelcluster",
    "taggit",
    "wagtail.contrib.settings",
    "wagtail.contrib.styleguide",
    "wagtail.contrib.modeladmin",
    "django.contrib.sitemaps",
    "wagtailautocomplete",
    "mapwidgets",
    "slippers",
    "wagtailmenus",
]

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "app.middleware.StagingDomainRedirectMiddleware",
    "livereload.middleware.LiveReloadScript",
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
    # wagtail-localize
    "django.middleware.locale.LocaleMiddleware",
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
]

ROOT_URLCONF = "app.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(PROJECT_DIR, "templates"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "wagtail.contrib.settings.context_processors.settings",
            ],
        },
    },
]

WSGI_APPLICATION = "app.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

PLATFORM_DATABASE_URL = os.getenv("DATABASE_URL", None)

if os.getenv("SKIP_DB") != "1" and isinstance(PLATFORM_DATABASE_URL, str):
    DATABASES = {
        "default": dj_database_url.parse(
            re.sub(r"^postgres(ql)?", "postgis", PLATFORM_DATABASE_URL),
            conn_max_age=600,
            ssl_require=False,
        )
    }

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

AUTH_USER_MODEL = "app.User"


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "en"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

WAGTAIL_I18N_ENABLED = True

# Allow any language that Django supports
WAGTAIL_CONTENT_LANGUAGES = LANGUAGES = [
    (locale[0], locale[1]["name_local"] + " (" + locale[1]["name"] + ")")
    for locale in LANG_INFO.items()
    if locale[1].get("name_local", None) and locale[1].get("name", None)
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]


DJANGO_VITE_ASSETS_PATH = BASE_DIR + "/vite"
DJANGO_VITE_MANIFEST_PATH = DJANGO_VITE_ASSETS_PATH + "/manifest.json"

STATICFILES_DIRS = [
    DJANGO_VITE_ASSETS_PATH,
]


# ManifestStaticFilesStorage is recommended in production, to prevent outdated
# JavaScript / CSS assets being served from cache (e.g. after a Wagtail upgrade).
# See https://docs.djangoproject.com/en/3.2/ref/contrib/staticfiles/#manifeststaticfilesstorage
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"

# The absolute path to the directory where collectstatic will collect static files for deployment.
STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATIC_URL = "/static/"

MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "/media/"


DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ]
}


# Logging

DJANGO_LOG_LEVEL = os.getenv("DJANGO_LOG_LEVEL", "INFO")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "": {
            "handlers": ["console"],
            "level": DJANGO_LOG_LEVEL,
        },
    },
}

INTERNAL_IPS = [
    "127.0.0.1",
]

BASE_URL = re.sub(r"/$", "", os.getenv("BASE_URL", "http://localhost:8000"))

# wagtail
WAGTAILADMIN_BASE_URL = os.getenv("WAGTAILADMIN_BASE_URL", BASE_URL)
WAGTAIL_SITE_NAME = "Humanitarian OpenStreetMap Team"
WAGTAILIMAGES_IMAGE_MODEL = "app.CMSImage"
WAGTAILDOCS_DOCUMENT_MODEL = "app.CMSDocument"

# cms
SETUP_DEMO_PAGES = os.getenv("SETUP_DEMO_PAGES", False)

# wagtail-localize
DEEPL_API_KEY = os.getenv("DEEPL_API_KEY", None)
if DEEPL_API_KEY is not None:
    WAGTAILLOCALIZE_MACHINE_TRANSLATOR = {
        "CLASS": "wagtail_localize.machine_translators.deepl.DeepLTranslator",
        "OPTIONS": {
            "AUTH_KEY": DEEPL_API_KEY,
        },
    }

# CSP
X_FRAME_OPTIONS = "SAMEORIGIN"

# Mapbox
MAPBOX_PUBLIC_API_KEY = os.getenv("MAPBOX_PUBLIC_API_KEY", None)

# for django-map-widgets
MAP_WIDGETS = {
    "MapboxPointFieldWidget": (("access_token", MAPBOX_PUBLIC_API_KEY),),
    "MAPBOX_API_KEY": MAPBOX_PUBLIC_API_KEY,
}

# Posthog
POSTHOG_PUBLIC_TOKEN = os.getenv("POSTHOG_PUBLIC_TOKEN", None)
POSTHOG_URL = os.getenv("POSTHOG_URL", "https://app.posthog.com")

if POSTHOG_PUBLIC_TOKEN is not None:
    posthog.project_api_key = POSTHOG_PUBLIC_TOKEN
    posthog.host = POSTHOG_URL
    POSTHOG_DJANGO = {"distinct_id": lambda request: request.user and request.user.id}
if POSTHOG_PUBLIC_TOKEN is None:
    posthog.disabled = True

# Github
GIT_SHA = os.getenv("GIT_SHA", None)

# Fly
FLY_APP_NAME = os.getenv("FLY_APP_NAME", None)

# Sentry
SENTRY_DSN = os.getenv("SENTRY_DSN", None)
SENTRY_ORG_SLUG = os.getenv("SENTRY_ORG_SLUG", None)
SENTRY_PROJECT_ID = os.getenv("SENTRY_PROJECT_ID", None)
SENTRY_TRACE_SAMPLE_RATE = float(os.getenv("SENTRY_TRACE_SAMPLE_RATE", 0.25))

if SENTRY_DSN is not None:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    integrations = [DjangoIntegration()]

    if POSTHOG_PUBLIC_TOKEN is not None and SENTRY_PROJECT_ID is not None:
        from posthog.sentry.posthog_integration import (
            PostHogIntegration as PostHogSentryIntegration,
        )

        PostHogSentryIntegration.organization = SENTRY_ORG_SLUG
        integrations += [PostHogSentryIntegration()]

        MIDDLEWARE += [
            "posthog.sentry.django.PosthogDistinctIdMiddleware",
        ]

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=integrations,
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production.
        traces_sample_rate=SENTRY_TRACE_SAMPLE_RATE,
        # If you wish to associate users to errors (assuming you are using
        # django.contrib.auth) you may enable sending PII data.
        send_default_pii=True,
        environment=FLY_APP_NAME,
        release=GIT_SHA,
    )

# debugging

USE_SILK = os.getenv("USE_SILK", False) in (True, "True", "true", "t", 1)

if USE_SILK:
    MIDDLEWARE += [
        "silk.middleware.SilkyMiddleware",
    ]

    INSTALLED_APPS += [
        "silk",
    ]

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "django_cache",
        "TIMEOUT": None,  # don't expire by default
    }
}

# REST API settings

WAGTAILAPI_LIMIT_MAX = None

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Humanitarian OpenStreetMap Team CMS API",
    "DESCRIPTION": "Access to the content management system for the HOTOSM website.",
    "VERSION": "1.0.0",
    "PREPROCESSING_HOOKS": ["app.api.preprocessing_hooks"],
}

# This is for redirecting. See app.middleware.StagingDomainRedirectMiddleware
REDIRECT_FROM_HOSTS = os.getenv("REDIRECT_FROM_HOSTS", "hotosm-staging.fly.dev").split(
    ","
)

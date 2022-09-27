import os
import re

import dj_database_url
from django.conf.locale import LANG_INFO

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(PROJECT_DIR)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/


# Application definition

INSTALLED_APPS = [
    "app",
    "anymail",
    "rest_framework",
    "groundwork.core",
    "groundwork.geo",
    "livereload",
    "debug_toolbar",
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
    "modelcluster",
    "taggit",
    "wagtail.contrib.settings",
    "wagtail.contrib.styleguide",
    "wagtail.contrib.modeladmin",
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
    "debug_toolbar.middleware.DebugToolbarMiddleware",
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
                "wagtailmenus.context_processors.wagtailmenus",
            ],
        },
    },
]

WSGI_APPLICATION = "app.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.parse(
            re.sub(r"^postgres(ql)?", "postgis", DATABASE_URL),
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

LANGUAGE_CODE = "en-gb"

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

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
WAGTAILADMIN_BASE_URL = os.getenv("WAGTAILADMIN_BASE_URL", BASE_URL)


# Wagtail
WAGTAIL_SITE_NAME = "Humanitarian OpenStreetMap Team"
WAGTAILIMAGES_IMAGE_MODEL = "app.CMSImage"
WAGTAILDOCS_DOCUMENT_MODEL = "app.CMSDocument"

# cms
SETUP_DEMO_PAGES = os.getenv("SETUP_DEMO_PAGES", True)

# wagtailmenus
WAGTAILMENUS_FLAT_MENUS_HANDLE_CHOICES = (("footer", "Footer"),)

# wagtail-localize
DEEPL_API_KEY = os.getenv("DEEPL_API_KEY", None)
if DEEPL_API_KEY is not None:
    WAGTAILLOCALIZE_MACHINE_TRANSLATOR = {
        "CLASS": "wagtail_localize.machine_translators.deepl.DeepLTranslator",
        "OPTIONS": {
            "AUTH_KEY": DEEPL_API_KEY,
        },
    }

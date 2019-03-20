import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ALLOWED_HOSTS = ["*"]

SECRET_KEY = "fake-key"
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "microsoft_auth",
    "tests",
]

try:
    import djangoql  # noqa

    INSTALLED_APPS.append("djangoql")
except ImportError:
    pass

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}

ROOT_URLCONF = "tests.site.urls"

LANGUAGE_CODE = "en-us"

STATIC_URL = "/static/"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

USE_I18N = True

USE_L10N = True

LANGUAGE_CODE = "en-us"

# this much be after the majority of your other settings
from microsoft_auth.conf import DEFAULT_CONFIG  # isort:skip # noqa

CONSTANCE_BACKEND = "constance.backends.database.DatabaseBackend"
CONSTANCE_CONFIG = DEFAULT_CONFIG["defaults"]
CONSTANCE_CONFIG_FIELDSETS = DEFAULT_CONFIG["fieldsets"]
CONSTANCE_ADDITIONAL_FIELDS = DEFAULT_CONFIG["fields"]

#####
# Do not commit these uncommented, they are for development purposes only
#####

# DEBUG = True
# TEMPLATES[0]["OPTIONS"]["context_processors"] += [
#     "microsoft_auth.context_processors.microsoft"
# ]

# AUTHENTICATION_BACKENDS = [
#     "microsoft_auth.backends.MicrosoftAuthenticationBackend",
#     "django.contrib.auth.backends.ModelBackend",
# ]

# INSTALLED_APPS += ["constance", "constance.backends.database"]

# from .local import *

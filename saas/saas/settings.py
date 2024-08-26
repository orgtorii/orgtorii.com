"""
Django settings.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

import os
import sys
import tempfile
from email.utils import getaddresses
from pathlib import Path

import environ

env = environ.Env(DEBUG=(bool, False))

PROJECT_DISPLAY_NAME = "SaaS Kit"  # Used for public display e.g as default in <title> tags
PROJECT_SLUG = "saas_kit"

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

environ.Env.read_env(os.path.join(BASE_DIR, ".env"))
environ.Env.read_env(os.path.join(BASE_DIR, ".env.local"))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str("SECRET_KEY")

DEBUG = env("DEBUG")

TESTING = "test" in sys.argv

ALLOWED_HOSTS = []

INTERNAL_IPS = [
    "127.0.0.1",
]

SITE_ID = 1

ADMINS = getaddresses([env("DJANGO_ADMINS")])

# Application definition

AUTH_USER_MODEL = "users.SaaSUser"

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "guardian",  # Object level permissions
    "django_filters",  # Filtering based on user input
    "django_extensions",  # Additional django extensions
    "allauth",  # Authentication
    "allauth.account",
    "allauth.mfa",  # Multi-factor authentication extension
    "meta",  # SEO metadata
    "djstripe",  # Stripe integration
    # Project apps
    "saas.users",
    "saas.core",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # allauth account middleware:
    "allauth.account.middleware.AccountMiddleware",
]

if not TESTING:
    # Don't add debug toolbar in testing mode
    # https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#disable-the-toolbar-when-running-tests-optional
    INSTALLED_APPS = [
        *INSTALLED_APPS,
        "debug_toolbar",
    ]
    MIDDLEWARE = [
        "debug_toolbar.middleware.DebugToolbarMiddleware",
        *MIDDLEWARE,
    ]

if not TESTING:
    # Don't add prometheus in testing mode
    INSTALLED_APPS = [
        *INSTALLED_APPS,
        "django_prometheus",
    ]
    MIDDLEWARE = [
        "django_prometheus.middleware.PrometheusBeforeMiddleware",
        *MIDDLEWARE,
        "django_prometheus.middleware.PrometheusAfterMiddleware",
    ]

ROOT_URLCONF = "saas.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "saas.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django_prometheus.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
        # https://gcollazo.com/optimal-sqlite-settings-for-django/
        "OPTIONS": {
            "init_command": (
                "PRAGMA foreign_keys=ON;"
                "PRAGMA journal_mode = WAL;"
                "PRAGMA synchronous = NORMAL;"
                "PRAGMA busy_timeout = 500;"  # 500ms
                "PRAGMA temp_store = MEMORY;"
                f"PRAGMA mmap_size = {128 * 1024 * 1024};"  # 128MB
                f"PRAGMA journal_size_limit = {64 * 1024 * 1024};"  # 64MB
                f"PRAGMA cache_size = -{8 * 1024 * 1024};"  # 8MB of 4096 bytes pages
            ),
            "transaction_mode": "IMMEDIATE",
        },
    }
}

# Cache
# https://docs.djangoproject.com/en/5.1/topics/cache/#using-a-custom-cache-backend
CACHES = {
    "default": {
        "BACKEND": "diskcache.DjangoCache",
        "LOCATION": os.path.join(tempfile.gettempdir(), f"{PROJECT_SLUG}-cache"),
        "TIMEOUT": 30,
        # ^-- Django setting for default timeout of each key.
        "SHARDS": 8,
        "DATABASE_TIMEOUT": 0.010,  # 10 milliseconds
        # ^-- Timeout for each DjangoCache database transaction.
        "OPTIONS": {"size_limit": 2**30},  # 1 gigabyte
    },
}

# Email settings
# https://docs.djangoproject.com/en/5.1/topics/email/
if env.bool("SEND_EMAILS") and not TESTING:
    pass
else:
    # Use console backend for development
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

DEFAULT_FROM_EMAIL = f"noreply@{env.str("EMAIL_DOMAIN")}"
SERVER_EMAIL = f"root@{env.str('EMAIL_DOMAIN')}"

# https://docs.djangoproject.com/en/dev/ref/settings/#email-timeout
EMAIL_TIMEOUT = 5

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 12,
        },
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

PASSWORD_HASHERS = [
    "saas.hashers.SecureArgon2PasswordHasher",
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
    "django.contrib.auth.hashers.ScryptPasswordHasher",
]

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",  # default
    "guardian.backends.ObjectPermissionBackend",
    # `allauth` specific authentication methods, such as login by email
    "allauth.account.auth_backends.AuthenticationBackend",
)

LOGIN_REDIRECT_URL = "account:dashboard"
LOGOUT_REDIRECT_URL = "home"

# Allauth user account settings
# https://docs.allauth.org/en/latest/account/configuration.html
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_CHANGE_EMAIL = True
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 1
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_DEFAULT_HTTP_PROTOCOL = "https"
ACCOUNT_LOGIN_BY_CODE_ENABLED = True
ACCOUNT_LOGIN_BY_CODE_TIMEOUT = 60 * 15  # 15 minutes
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_LOGIN_ON_PASSWORD_RESET = True
ACCOUNT_PRESERVE_USERNAME_CASING = False
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = False
ACCOUNT_USERNAME_BLACKLIST = []
ACCOUNT_USERNAME_MIN_LENGTH = 3
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_USER_MODEL_USERNAME_FIELD = None

# https://cookiecutter-django.readthedocs.io/en/latest/settings.html#other-environment-settings
# Force the `admin` sign in process to go through the `django-allauth` workflow
DJANGO_ADMIN_FORCE_ALLAUTH = True

# Allauth MFA settings
# https://docs.allauth.org/en/latest/mfa/webauthn.html

# Make sure "webauthn" is included.
MFA_SUPPORTED_TYPES = ["totp", "webauthn", "recovery_codes"]

# Optional: enable support for logging in using a (WebAuthn) passkey.
MFA_PASSKEY_LOGIN_ENABLED = True

# Optional -- use for local development only: the WebAuthn uses the
# ``fido2`` package, and versions up to including version 1.1.3 do not
# regard localhost as a secure origin, which is problematic during
# local development and testing.
MFA_WEBAUTHN_ALLOW_INSECURE_ORIGIN = DEBUG

MFA_TOTP_ISSUER = PROJECT_DISPLAY_NAME

# Django newsletter
# https://django-newsletter.readthedocs.io/en/latest/installation.html
# Using sorl-thumbnail
NEWSLETTER_THUMBNAIL = "sorl-thumbnail"

# Django meta settings
# https://django-meta.readthedocs.io/en/latest/settings.html
META_SITE_PROTOCOL = "https"
if DEBUG:
    META_SITE_PROTOCOL = "http"
META_SITE_TYPE = "website"
META_SITE_NAME = PROJECT_DISPLAY_NAME
META_USE_TITLE_TAG = False
META_USE_OG_PROPERTIES = True
META_USE_TWITTER_PROPERTIES = True
META_USE_SITES = True

# Django Stripe settings
# https://dj-stripe.dev/2.8/reference/settings/
STRIPE_LIVE_SECRET_KEY = env.str("STRIPE_LIVE_SECRET_KEY")
STRIPE_TEST_SECRET_KEY = env.str("STRIPE_TEST_SECRET_KEY")
STRIPE_LIVE_MODE = env.bool("STRIPE_LIVE_MODE")
DJSTRIPE_WEBHOOK_SECRET = env.str("STRIPE_WEBHOOK_SECRET")
DJSTRIPE_FOREIGN_KEY_TO_FIELD = "id"

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# https://docs.djangoproject.com/en/5.1/ref/templates/builtins/#std-templatefilter-date
DATE_FORMAT = "d E Y"
SHORT_DATE_FORMAT = "Y/m/d"
DATETIME_FORMAT = "d E Y H:i:s"
SHORT_DATETIME_FORMAT = "Y/m/d H:i"

USE_THOUSAND_SEPARATOR = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

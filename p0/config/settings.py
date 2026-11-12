"""Nastavitve P0. Vse občutljive vrednosti pridejo iz okolja; nič ni v repozitoriju."""

import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

from config.checks import stubs_in_production

BASE_DIR = Path(__file__).resolve().parent.parent


def env(name, default=None, required=False):
    value = os.environ.get(name, default)
    if required and not value:
        raise ImproperlyConfigured(f"Manjka spremenljivka okolja {name}")
    return value


DEBUG = env("DJANGO_DEBUG", "0") == "1"

SECRET_KEY = env("DJANGO_SECRET_KEY", "razvoj-ni-za-produkcijo" if DEBUG else None, required=True)

ALLOWED_HOSTS = [h for h in env("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",") if h]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "allauth",
    "allauth.account",
    "core",
    "registry",
    "stubs",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "core.middleware.ApiErrorMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Nadomestka modulov (stubs): privzeto samo v razvoju. Ko ekipa vgradi pravi modul, ga
# odstrani s seznama, npr. STUBS=m2 (nadomestek M1 izklopljen).
STUBS = {x.strip() for x in env("STUBS", "m1,m2" if DEBUG else "").split(",") if x.strip()}
if stubs_in_production(DEBUG, STUBS):
    raise ImproperlyConfigured(
        "STUBS je dovoljen samo z DJANGO_DEBUG=1 (nadomestka nista za produkcijo)."
    )

AUTH_USER_MODEL = "registry.Account"

CSRF_FAILURE_VIEW = "core.views.csrf_failure"

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("POSTGRES_DB", "p0"),
        "USER": env("POSTGRES_USER", "p0"),
        "PASSWORD": env("POSTGRES_PASSWORD", "p0-razvoj" if DEBUG else None, required=True),
        "HOST": env("POSTGRES_HOST", "localhost"),
        "PORT": env("POSTGRES_PORT", "5432"),
    }
}

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

# Prijava s uporabniškim imenom: e-naslov ni identiteta in ni enoličen (skupni predal staršev).
ACCOUNT_LOGIN_METHODS = {"username"}
ACCOUNT_SIGNUP_FIELDS = ["username*", "password1*", "password2*"]
ACCOUNT_UNIQUE_EMAIL = False
ACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_ADAPTER = "registry.adapters.ClosedAccountAdapter"
ACCOUNT_LOGOUT_ON_GET = False
LOGIN_REDIRECT_URL = "/p0/api/v1/me"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Jezik vmesnika slovenščina; podatkovni model je večjezičen od začetka (D05).
LANGUAGE_CODE = "sl"
TIME_ZONE = "Europe/Ljubljana"  # prikaz in urniki; shranjevanje je v UTC (USE_TZ)
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Razvojna pošta gre vedno v prestrezni predal (Mailpit); resnična dostava se ne zgodi.
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env("EMAIL_HOST", "localhost")
EMAIL_PORT = int(env("EMAIL_PORT", "1025"))

if not DEBUG:
    SESSION_COOKIE_SECURE = env("DJANGO_INSECURE_COOKIES", "0") != "1"
    CSRF_COOKIE_SECURE = SESSION_COOKIE_SECURE
    SECURE_CONTENT_TYPE_NOSNIFF = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"

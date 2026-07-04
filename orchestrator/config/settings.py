"""Django settings for the orchestrator. All secrets/config via environment."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def env(key: str, default: str | None = None) -> str:
  value = os.environ.get(key, default)
  if value is None:
    raise RuntimeError(f"Missing required environment variable: {key}")
  return value


def env_bool(key: str, default: bool = False) -> bool:
  return os.environ.get(key, str(default)).lower() in ("1", "true", "yes")


SECRET_KEY = env("DJANGO_SECRET_KEY", "insecure-dev-key-change-me")
DEBUG = env_bool("DJANGO_DEBUG", False)
ALLOWED_HOSTS = [h.strip() for h in env("DJANGO_ALLOWED_HOSTS", "localhost").split(",") if h.strip()]

# Fernet key used by common.fields.EncryptedTextField to encrypt tokens at rest.
FIELD_ENCRYPTION_KEY = env("FIELD_ENCRYPTION_KEY", "")

# Behind Caddy, which terminates TLS.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
CSRF_TRUSTED_ORIGINS = [f"https://{h}" for h in ALLOWED_HOSTS if h != "localhost"]

INSTALLED_APPS = [
  "django.contrib.admin",
  "django.contrib.auth",
  "django.contrib.contenttypes",
  "django.contrib.sessions",
  "django.contrib.messages",
  "django.contrib.staticfiles",
  "rest_framework",
  "common",
  "accounts",
  "mirrors",
  "destinations",
  "syncjobs",
]

MIDDLEWARE = [
  "django.middleware.security.SecurityMiddleware",
  "whitenoise.middleware.WhiteNoiseMiddleware",
  "django.contrib.sessions.middleware.SessionMiddleware",
  "django.middleware.common.CommonMiddleware",
  "django.middleware.csrf.CsrfViewMiddleware",
  "django.contrib.auth.middleware.AuthenticationMiddleware",
  "django.contrib.messages.middleware.MessageMiddleware",
  "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [
  {
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [],
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

DATABASES = {
  "default": {
    "ENGINE": "django.db.backends.postgresql",
    "NAME": env("POSTGRES_DB", "orchestrator"),
    "USER": env("POSTGRES_USER", "orchestrator"),
    "PASSWORD": env("POSTGRES_PASSWORD", ""),
    "HOST": env("POSTGRES_HOST", "db"),
    "PORT": env("POSTGRES_PORT", "5432"),
  }
}

REST_FRAMEWORK = {
  "DEFAULT_AUTHENTICATION_CLASSES": [
    "rest_framework.authentication.SessionAuthentication",
  ],
  "DEFAULT_PERMISSION_CLASSES": [
    "rest_framework.permissions.IsAdminUser",
  ],
}

# Forgejo + sync configuration.
FORGEJO_API_URL = env("FORGEJO_API_URL", "http://forgejo:3000")
FORGEJO_ADMIN_TOKEN = env("FORGEJO_ADMIN_TOKEN", "")
DISCOVERY_INTERVAL_HOURS = int(env("DISCOVERY_INTERVAL_HOURS", "6"))
MAX_REPO_SIZE_MB = int(env("MAX_REPO_SIZE_MB", "2048"))
DISK_PAUSE_THRESHOLD_PERCENT = int(env("DISK_PAUSE_THRESHOLD_PERCENT", "90"))

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
  "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
  "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
TIME_ZONE = os.environ.get("TZ", "UTC")
USE_TZ = True
LANGUAGE_CODE = "en-us"

LOGGING = {
  "version": 1,
  "disable_existing_loggers": False,
  "handlers": {"console": {"class": "logging.StreamHandler"}},
  "root": {"handlers": ["console"], "level": "INFO"},
}

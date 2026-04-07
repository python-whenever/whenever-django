from __future__ import annotations

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "whenever_django",
    "tests",
]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
USE_TZ = True

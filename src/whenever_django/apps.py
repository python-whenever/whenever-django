from __future__ import annotations

from django.apps import AppConfig


class WheneverDjangoConfig(AppConfig):
    name = "whenever_django"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self) -> None:
        from .lookups import register_lookups

        register_lookups()

        try:
            from .contrib.drf.fields import register_field_mapping

            register_field_mapping()
        except ImportError:
            # DRF not installed
            pass

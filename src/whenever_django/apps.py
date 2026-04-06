from __future__ import annotations

from django.apps import AppConfig


class WheneverDjangoConfig(AppConfig):
    name = "whenever_django"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self) -> None:
        from .lookups import register_lookups

        register_lookups()

        from ._compat import HAS_REST_FRAMEWORK

        if HAS_REST_FRAMEWORK:
            from .contrib.drf import register_serializer_fields

            register_serializer_fields()

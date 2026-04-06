from __future__ import annotations

from django.apps import apps
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Audit models for stdlib datetime fields that can be replaced with whenever fields."

    FIELD_MAPPING: dict[str, str] = {
        "DateTimeField": "InstantField (or PlainDateTimeField for naive)",
        "DateField": "WheneverDateField",
        "TimeField": "WheneverTimeField",
        "DurationField": "TimeDeltaField",
    }

    def add_arguments(self, parser: object) -> None:
        parser.add_argument(  # type: ignore[attr-defined]
            "--app-label",
            type=str,
            help="Limit scan to a specific app label.",
        )

    def handle(self, *args: object, **options: object) -> None:
        app_label: str | None = options.get("app_label")  # type: ignore[assignment]

        if app_label:
            try:
                app_config = apps.get_app_config(app_label)
                models_to_scan = app_config.get_models()
            except LookupError:
                self.stderr.write(f"App '{app_label}' not found.")
                return
        else:
            models_to_scan = apps.get_models()

        findings: list[dict[str, str]] = []
        for model in models_to_scan:
            for field in model._meta.get_fields():
                field_type = type(field).__name__
                if field_type in self.FIELD_MAPPING:
                    findings.append({
                        "app": model._meta.app_label,
                        "model": model.__name__,
                        "field": field.name,
                        "current_type": field_type,
                        "recommended": self.FIELD_MAPPING[field_type],
                    })

        if not findings:
            self.stdout.write(
                self.style.SUCCESS("No stdlib datetime fields found. Nothing to convert.")
            )
            return

        self.stdout.write(self.style.MIGRATE_HEADING("\nwhenever-django Migration Audit Report"))
        self.stdout.write(self.style.MIGRATE_HEADING("=" * 50))

        for f in findings:
            self.stdout.write(
                f"  {f['app']}.{f['model']}.{f['field']}: "
                f"{f['current_type']} -> {f['recommended']}"
            )

        self.stdout.write(f"\nFound {len(findings)} field(s) that can be converted.")

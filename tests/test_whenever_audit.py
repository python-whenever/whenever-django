"""Tests for the whenever_audit management command."""
from __future__ import annotations

from io import StringIO

from django.core.management import call_command
from django.db import models


class AuditTestModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    date = models.DateField(null=True)
    time = models.TimeField(null=True)
    duration = models.DurationField(null=True)
    name = models.CharField(max_length=100)

    class Meta:
        app_label = "tests"


class TestWheneverAudit:
    def test_audit_finds_datetime_fields(self) -> None:
        out = StringIO()
        call_command("whenever_audit", "--app-label", "tests", stdout=out)
        output = out.getvalue()

        assert "DateTimeField" in output
        assert "DateField" in output
        assert "TimeField" in output
        assert "DurationField" in output

    def test_audit_ignores_non_datetime_fields(self) -> None:
        out = StringIO()
        call_command("whenever_audit", "--app-label", "tests", stdout=out)
        output = out.getvalue()

        assert "CharField" not in output
        assert ".name:" not in output

    def test_audit_app_label_filter(self) -> None:
        out = StringIO()
        call_command("whenever_audit", "--app-label", "tests", stdout=out)
        output = out.getvalue()

        # Only fields from the "tests" app should appear
        for line in output.splitlines():
            if "->" in line:
                assert line.strip().startswith("tests.")

    def test_audit_invalid_app_label(self) -> None:
        err = StringIO()
        call_command("whenever_audit", "--app-label", "nonexistent_app_xyz", stderr=err)
        assert "not found" in err.getvalue()

    def test_audit_no_findings(self) -> None:
        """whenever_django app has no stdlib datetime fields."""
        out = StringIO()
        call_command("whenever_audit", "--app-label", "whenever_django", stdout=out)
        assert "No stdlib datetime fields found" in out.getvalue()

"""Validate required source fields and their basic shape."""

from collections.abc import Iterable

from app.market_data.models.data_quality import Severity, ValidationReport

REQUIRED = ("timestamp", "open", "high", "low", "close")


class StructuralValidator:
    def validate(self, records: Iterable[dict]) -> ValidationReport:
        report = ValidationReport()
        for index, record in enumerate(records):
            report.records_checked += 1
            if not isinstance(record, dict):
                report.add("RECORD_NOT_MAPPING", Severity.ERROR, f"Record {index} is not a mapping")
                continue
            missing = [name for name in REQUIRED if name not in record]
            if missing:
                report.add("MISSING_REQUIRED_FIELD", Severity.ERROR, f"Record {index} is missing: {', '.join(missing)}")
            for name in REQUIRED:
                if name in record and record[name] is None:
                    report.add("NULL_REQUIRED_FIELD", Severity.ERROR, f"Record {index} has null {name}")
        return report

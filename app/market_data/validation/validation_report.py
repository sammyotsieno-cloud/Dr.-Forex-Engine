"""Validation report composition."""

from app.market_data.models.data_quality import ValidationReport


class ValidationReportBuilder:
    @staticmethod
    def combine(*reports: ValidationReport) -> ValidationReport:
        result = ValidationReport()
        for report in reports:
            result.records_checked = max(result.records_checked, report.records_checked)
            result.findings.extend(report.findings)
        return result

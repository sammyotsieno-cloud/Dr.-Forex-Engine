"""Quality findings and validation status."""

from dataclasses import dataclass, field
from enum import StrEnum


class Severity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass(frozen=True, slots=True)
class QualityFinding:
    code: str
    severity: Severity
    message: str
    timestamp: str | None = None


@dataclass(slots=True)
class ValidationReport:
    """Evidence produced by validation; no invalid record is silently repaired."""

    findings: list[QualityFinding] = field(default_factory=list)
    records_checked: int = 0

    @property
    def errors(self) -> list[QualityFinding]:
        return [item for item in self.findings if item.severity == Severity.ERROR]

    @property
    def warnings(self) -> list[QualityFinding]:
        return [item for item in self.findings if item.severity == Severity.WARNING]

    @property
    def is_valid(self) -> bool:
        return not self.errors

    def add(self, code: str, severity: Severity, message: str, timestamp: str | None = None) -> None:
        self.findings.append(QualityFinding(code, severity, message, timestamp))

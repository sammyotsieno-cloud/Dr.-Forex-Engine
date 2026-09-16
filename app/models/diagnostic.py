from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from app.models.repair import RepairProposal, VerificationPlan


class FailureType(str, Enum):
    INSTALLATION = "installation"
    IMPORT = "import"
    TEST = "test"
    PACKAGE = "package"
    WORKFLOW = "workflow"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class FailureLocation:
    file: str | None = None
    line: int | None = None
    function: str | None = None


@dataclass
class DiagnosticEvidence:
    source: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class DiagnosticFailure:
    failure_type: FailureType
    message: str
    location: FailureLocation = field(default_factory=FailureLocation)
    step: str | None = None
    evidence_sources: list[str] = field(default_factory=list)


@dataclass
class RootCause:
    description: str
    evidence: list[str] = field(default_factory=list)
    confidence: float = 0.0
    primary: bool = False


@dataclass
class DiagnosticFinding:
    category: str
    description: str
    severity: str = "info"
    evidence: list[str] = field(default_factory=list)


@dataclass
class DiagnosticReport:
    failures: list[DiagnosticFailure] = field(default_factory=list)
    root_causes: list[RootCause] = field(default_factory=list)
    findings: list[DiagnosticFinding] = field(default_factory=list)
    intent_consistent: bool = True
    confidence: float = 0.0
    unknowns: list[str] = field(default_factory=list)
    repair_proposal: RepairProposal | None = None
    verification_plan: VerificationPlan | None = None


@dataclass
class EvidenceBundle:
    files: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def add(self, name: str, content: str) -> None:
        self.files[name] = content

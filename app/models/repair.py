from dataclasses import dataclass, field


@dataclass
class FileChange:
    path: str
    reason: str
    functions: list[str] = field(default_factory=list)


@dataclass
class RepairProposal:
    summary: str
    changes: list[FileChange] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)
    verification_requirements: list[str] = field(default_factory=list)
    intent_preserved: bool = True


@dataclass
class VerificationPlan:
    checks: list[str] = field(default_factory=list)
    success_conditions: list[str] = field(default_factory=list)
    failure_conditions: list[str] = field(default_factory=list)

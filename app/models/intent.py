from dataclasses import dataclass, field
from typing import Any


@dataclass
class UserIntent:
    objective: str
    objectives: list[str] = field(default_factory=list)
    desired_capabilities: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    prohibited_changes: list[str] = field(default_factory=list)
    affected_components: list[str] = field(default_factory=list)
    measurement_criteria: list[str] = field(default_factory=list)
    acceptance_criteria: list[str] = field(default_factory=list)
    source_statements: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ProjectIntent:
    objectives: list[str] = field(default_factory=list)
    required_capabilities: list[str] = field(default_factory=list)
    protected_capabilities: list[str] = field(default_factory=list)
    architectural_constraints: list[str] = field(default_factory=list)
    dependency_expectations: dict[str, list[str]] = field(default_factory=dict)


@dataclass
class IntentAssessment:
    consistent: bool
    capability_loss: list[str] = field(default_factory=list)
    architectural_violations: list[str] = field(default_factory=list)
    scope_creep: list[str] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)
    preserved_intentions: list[str] = field(default_factory=list)

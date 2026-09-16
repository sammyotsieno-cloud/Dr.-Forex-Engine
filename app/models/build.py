from dataclasses import dataclass, field


@dataclass
class BuildStep:
    name: str
    outcome: str
    log_path: str | None = None


@dataclass
class BuildRun:
    run_number: str | None = None
    commit_sha: str | None = None
    branch: str | None = None
    workflow: str | None = None
    trigger: str | None = None
    steps: list[BuildStep] = field(default_factory=list)
    artifacts: list[str] = field(default_factory=list)


@dataclass
class BuildResult:
    success: bool
    failed_step: str | None = None
    run: BuildRun | None = None

"""Small structured trace boundary for reproducible engine runs."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True, slots=True)
class TraceEvent:
    name: str
    timestamp: datetime
    details: tuple[tuple[str, str], ...] = ()


@dataclass(slots=True)
class RunTrace:
    """Append-only execution history for research, replay and diagnostics."""

    run_id: str
    events: list[TraceEvent] = field(default_factory=list)

    def record(self, name: str, **details: Any) -> TraceEvent:
        if not name.strip():
            raise ValueError("trace event name must not be empty")
        event = TraceEvent(
            name=name,
            timestamp=datetime.now(timezone.utc),
            details=tuple(sorted((key, str(value)) for key, value in details.items())),
        )
        self.events.append(event)
        return event

    def snapshot(self) -> tuple[TraceEvent, ...]:
        return tuple(self.events)

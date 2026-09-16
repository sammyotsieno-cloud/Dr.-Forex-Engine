"""Tests for deterministic and auditable future-workflow boundaries."""

from datetime import datetime, timezone

import pytest

from app.core.run_trace import RunTrace
from app.core.simulation_clock import SimulationClock


def test_simulation_clock_advances_only_forward():
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    clock = SimulationClock(start)
    assert clock.current == start
    assert clock.advance_to(datetime(2026, 1, 1, 1, tzinfo=timezone.utc)).hour == 1
    with pytest.raises(ValueError):
        clock.advance_to(start)


def test_run_trace_is_append_only_and_structured():
    trace = RunTrace("EXP-000001")
    event = trace.record("dataset_validated", fingerprint="abc123", records=10)
    assert event.name == "dataset_validated"
    assert event.details == (("fingerprint", "abc123"), ("records", "10"))
    snapshot = trace.snapshot()
    assert len(snapshot) == 1
    assert snapshot[0] is event

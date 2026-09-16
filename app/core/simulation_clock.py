"""Deterministic time boundary for future simulation and replay."""

from datetime import datetime, timezone


class SimulationClock:
    """A clock whose time advances only when the engine advances it.

    Research and backtesting code must not depend on wall-clock ``now()`` when
    replaying historical observations. Live execution can use a separate clock
    later without changing strategy-facing time semantics.
    """

    def __init__(self, start: datetime) -> None:
        self._current = self._normalize(start)

    @property
    def current(self) -> datetime:
        return self._current

    def advance_to(self, timestamp: datetime) -> datetime:
        next_time = self._normalize(timestamp)
        if next_time < self._current:
            raise ValueError("simulation clock cannot move backwards")
        self._current = next_time
        return self._current

    @staticmethod
    def _normalize(timestamp: datetime) -> datetime:
        if timestamp.tzinfo is None or timestamp.utcoffset() is None:
            raise ValueError("simulation clock timestamps must be timezone-aware")
        return timestamp.astimezone(timezone.utc)

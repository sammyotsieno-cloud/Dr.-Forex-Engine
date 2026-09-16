"""Temporal validation: ordering, duplicates and unexpected gaps."""

from collections.abc import Iterable
from datetime import timedelta

from app.market_data.models.data_quality import Severity, ValidationReport
from app.market_data.models.market_bar import MarketBar


_TIMEFRAME_MINUTES = {
    "1m": 1, "5m": 5, "15m": 15, "30m": 30,
    "1h": 60, "4h": 240, "1d": 1440,
}


def timeframe_delta(timeframe: str) -> timedelta | None:
    minutes = _TIMEFRAME_MINUTES.get(timeframe.strip().lower())
    return timedelta(minutes=minutes) if minutes is not None else None


class TemporalValidator:
    def validate(self, bars: Iterable[MarketBar]) -> ValidationReport:
        ordered = list(bars)
        report = ValidationReport(records_checked=len(ordered))
        previous = None
        expected = timeframe_delta(ordered[0].timeframe) if ordered else None
        for bar in ordered:
            current = bar.utc_timestamp
            if previous is not None:
                if current < previous:
                    report.add("OUT_OF_ORDER", Severity.ERROR, "Timestamps are not chronological", current.isoformat())
                elif current == previous:
                    report.add("DUPLICATE_TIMESTAMP", Severity.ERROR, "Duplicate timestamp", current.isoformat())
                elif expected is not None and current - previous > expected:
                    report.add("DATA_GAP", Severity.WARNING, f"Gap exceeds expected {bar.timeframe} interval", current.isoformat())
            previous = current
        return report

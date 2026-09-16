"""Detect missing fixed-timeframe observations."""

from app.market_data.models.data_quality import Severity, ValidationReport
from app.market_data.models.market_bar import MarketBar
from app.market_data.validation.temporal_validator import timeframe_delta


class GapDetector:
    def detect(self, bars: list[MarketBar]) -> ValidationReport:
        report = ValidationReport(records_checked=len(bars))
        if len(bars) < 2:
            return report
        delta = timeframe_delta(bars[0].timeframe)
        if delta is None:
            report.add("UNKNOWN_TIMEFRAME", Severity.WARNING, f"Gap detection is not defined for {bars[0].timeframe!r}")
            return report
        for previous, current in zip(bars, bars[1:]):
            difference = current.utc_timestamp - previous.utc_timestamp
            if difference > delta:
                missing = max(int(difference / delta) - 1, 1)
                report.add("DATA_GAP", Severity.WARNING, f"At least {missing} observation(s) missing", current.utc_timestamp.isoformat())
        return report

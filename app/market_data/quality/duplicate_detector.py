"""Detect duplicate timestamps without altering observations."""

from app.market_data.models.data_quality import Severity, ValidationReport
from app.market_data.models.market_bar import MarketBar


class DuplicateDetector:
    def detect(self, bars: list[MarketBar]) -> ValidationReport:
        report = ValidationReport(records_checked=len(bars))
        seen: set = set()
        for bar in bars:
            stamp = bar.utc_timestamp
            if stamp in seen:
                report.add("DUPLICATE_TIMESTAMP", Severity.ERROR, "Duplicate market observation", stamp.isoformat())
            seen.add(stamp)
        return report

"""Check requested period coverage without inventing missing observations."""

from app.market_data.models.data_quality import Severity, ValidationReport
from app.market_data.models.market_bar import MarketBar


class CompletenessChecker:
    def check(self, bars: list[MarketBar], requested_start, requested_end) -> ValidationReport:
        report = ValidationReport(records_checked=len(bars))
        if not bars:
            report.add("NO_DATA", Severity.ERROR, "No observations were returned")
            return report
        actual_start = bars[0].utc_timestamp
        actual_end = bars[-1].utc_timestamp
        start = requested_start.astimezone(actual_start.tzinfo)
        end = requested_end.astimezone(actual_end.tzinfo)
        if actual_start > start:
            report.add("START_COVERAGE_GAP", Severity.ERROR, "Returned data starts after the requested period", actual_start.isoformat())
        if actual_end < end:
            report.add("END_COVERAGE_GAP", Severity.ERROR, "Returned data ends before the requested period", actual_end.isoformat())
        return report

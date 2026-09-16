"""Flag suspicious price jumps as warnings; never repair them."""

from decimal import Decimal

from app.market_data.models.data_quality import Severity, ValidationReport
from app.market_data.models.market_bar import MarketBar


class AnomalyDetector:
    def __init__(self, max_close_to_close_ratio: Decimal = Decimal("0.20")) -> None:
        if max_close_to_close_ratio <= 0:
            raise ValueError("threshold must be positive")
        self.threshold = max_close_to_close_ratio

    def detect(self, bars: list[MarketBar]) -> ValidationReport:
        report = ValidationReport(records_checked=len(bars))
        for previous, current in zip(bars, bars[1:]):
            change = abs(current.close - previous.close) / previous.close
            if change > self.threshold:
                report.add("EXTREME_PRICE_MOVE", Severity.WARNING, f"Close-to-close change {change:.4%} exceeds threshold", current.utc_timestamp.isoformat())
        return report

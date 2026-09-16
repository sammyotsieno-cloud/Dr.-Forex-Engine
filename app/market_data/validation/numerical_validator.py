"""Numerical integrity checks for canonical market bars."""

from collections.abc import Iterable

from app.market_data.models.data_quality import Severity, ValidationReport
from app.market_data.models.market_bar import MarketBar


class NumericalValidator:
    def validate(self, bars: Iterable[MarketBar]) -> ValidationReport:
        report = ValidationReport()
        for bar in bars:
            report.records_checked += 1
            if bar.high < bar.low:
                report.add("HIGH_BELOW_LOW", Severity.ERROR, "High is below low", bar.utc_timestamp.isoformat())
            if bar.spread is not None and bar.bid is not None and bar.ask is not None:
                implied = bar.ask - bar.bid
                if bar.spread != implied:
                    report.add(
                        "SPREAD_MISMATCH",
                        Severity.ERROR,
                        "Reported spread does not equal ask minus bid",
                        bar.utc_timestamp.isoformat(),
                    )
        return report

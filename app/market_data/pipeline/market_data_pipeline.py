"""Single semantic pipeline from source observations to research-ready data."""

from app.market_data.models.data_quality import Severity, ValidationReport
from app.market_data.models.market_dataset import DatasetProvenance, MarketDataset
from app.market_data.models.instrument import Instrument
from app.market_data.normalization.market_data_normalizer import MarketDataNormalizer
from app.market_data.quality.anomaly_detector import AnomalyDetector
from app.market_data.quality.completeness_checker import CompletenessChecker
from app.market_data.quality.duplicate_detector import DuplicateDetector
from app.market_data.quality.gap_detector import GapDetector
from app.market_data.validation.numerical_validator import NumericalValidator
from app.market_data.validation.structural_validator import StructuralValidator
from app.market_data.validation.temporal_validator import TemporalValidator


class DataIntegrityError(ValueError):
    """Raised when Phase 1 cannot safely release data downstream."""

    def __init__(self, report: ValidationReport) -> None:
        self.report = report
        super().__init__(f"Market data failed integrity checks: {len(report.errors)} error(s)")


class MarketDataPipeline:
    """Acquire-independent Phase 1 processing pipeline.

    No stage silently repairs invalid observations. Errors stop the boundary;
    warnings remain attached to the dataset so downstream analysis can account
    for data limitations explicitly.
    """

    def __init__(self) -> None:
        self.structural = StructuralValidator()
        self.normalizer = MarketDataNormalizer()
        self.numerical = NumericalValidator()
        self.temporal = TemporalValidator()
        self.duplicates = DuplicateDetector()
        self.gaps = GapDetector()
        self.anomalies = AnomalyDetector()
        self.completeness = CompletenessChecker()

    def process(
        self,
        records: list[dict],
        instrument: Instrument,
        timeframe: str,
        provenance: DatasetProvenance,
    ) -> MarketDataset:
        structural = self.structural.validate(records)
        if not structural.is_valid:
            raise DataIntegrityError(structural)

        try:
            bars = self.normalizer.normalize(records, instrument, timeframe)
        except ValueError as exc:
            structural.add("NORMALIZATION_FAILURE", Severity.ERROR, str(exc))
            raise DataIntegrityError(structural) from exc

        reports = (
            self.numerical.validate(bars),
            self.temporal.validate(bars),
            self.duplicates.detect(bars),
            self.gaps.detect(bars),
            self.anomalies.detect(bars),
            self.completeness.check(bars, provenance.requested_start, provenance.requested_end),
        )
        report = ValidationReport(records_checked=len(bars))
        for item in reports:
            report.findings.extend(item.findings)

        if report.errors:
            raise DataIntegrityError(report)

        return MarketDataset(
            instrument=instrument,
            timeframe=timeframe,
            bars=bars,
            provenance=provenance,
            validation=report,
            normalized=True,
        )

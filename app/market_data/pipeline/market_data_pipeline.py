"""Single semantic boundary from acquisition to research-ready market data."""

from datetime import datetime, timezone

from app.market_data.acquisition.data_acquisition import DataAcquisition
from app.market_data.acquisition.data_request import DataRequest
from app.market_data.acquisition.data_source import MarketDataSource
from app.market_data.models.data_quality import Severity, ValidationReport
from app.market_data.models.market_dataset import DatasetProvenance, MarketDataset
from app.market_data.models.instrument import Instrument
from app.market_data.normalization.market_data_normalizer import MarketDataNormalizer
from app.market_data.quality.anomaly_detector import AnomalyDetector
from app.market_data.quality.completeness_checker import CompletenessChecker
from app.market_data.quality.duplicate_detector import DuplicateDetector
from app.market_data.quality.gap_detector import GapDetector
from app.market_data.raw.raw_data_store import RawDataStore
from app.market_data.validation.numerical_validator import NumericalValidator
from app.market_data.validation.structural_validator import StructuralValidator
from app.market_data.validation.temporal_validator import TemporalValidator


class DataIntegrityError(ValueError):
    """Raised when Phase 1 cannot safely release data downstream."""

    def __init__(self, report: ValidationReport) -> None:
        self.report = report
        super().__init__(f"Market data failed integrity checks: {len(report.errors)} error(s)")


class MarketDataPipeline:
    """Move observations through explicit integrity gates.

    Acquisition, raw preservation, validation, normalization and quality
    assessment are deliberately separate. Invalid observations are rejected;
    suspicious but non-fatal findings remain attached as warnings.
    """

    def __init__(self, raw_store: RawDataStore | None = None) -> None:
        self.acquisition = DataAcquisition()
        self.raw_store = raw_store or RawDataStore()
        self.structural = StructuralValidator()
        self.normalizer = MarketDataNormalizer()
        self.numerical = NumericalValidator()
        self.temporal = TemporalValidator()
        self.duplicates = DuplicateDetector()
        self.gaps = GapDetector()
        self.anomalies = AnomalyDetector()
        self.completeness = CompletenessChecker()

    def run(self, source: MarketDataSource, request: DataRequest) -> MarketDataset:
        acquired_at = datetime.now(timezone.utc)
        records = self.acquisition.acquire(source, request)
        self.raw_store.append(records)
        provenance = DatasetProvenance(
            source_name=source.name,
            requested_start=request.start,
            requested_end=request.end,
            acquired_at=acquired_at,
            source_reference=getattr(source, "source_reference", None),
            broker=getattr(source, "broker", None),
            server=getattr(source, "server", None),
            provider_symbol=request.instrument.provider_symbol or request.instrument.symbol,
        )
        return self.process(records, request.instrument, request.timeframe, provenance)

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
            self.numerical.validate(bars), self.temporal.validate(bars),
            self.duplicates.detect(bars), self.gaps.detect(bars),
            self.anomalies.detect(bars),
            self.completeness.check(bars, provenance.requested_start, provenance.requested_end),
        )
        report = ValidationReport(records_checked=len(bars))
        for item in reports:
            report.findings.extend(item.findings)
        if report.errors:
            raise DataIntegrityError(report)
        return MarketDataset(instrument, timeframe, bars, provenance, report, normalized=True)

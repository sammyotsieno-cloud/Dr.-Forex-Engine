"""Research-ready dataset and provenance metadata."""

from dataclasses import dataclass, field
from datetime import datetime

from app.market_data.models.instrument import Instrument
from app.market_data.models.market_bar import MarketBar
from app.market_data.models.data_quality import ValidationReport


@dataclass(frozen=True, slots=True)
class DatasetProvenance:
    source_name: str
    requested_start: datetime
    requested_end: datetime
    acquired_at: datetime
    source_reference: str | None = None
    broker: str | None = None
    server: str | None = None
    provider_symbol: str | None = None

    def __post_init__(self) -> None:
        for value in (self.requested_start, self.requested_end, self.acquired_at):
            if value.tzinfo is None or value.utcoffset() is None:
                raise ValueError("Dataset provenance timestamps must be timezone-aware")
        if self.requested_end < self.requested_start:
            raise ValueError("requested_end must not precede requested_start")
        if not self.source_name.strip():
            raise ValueError("source_name must not be empty")


@dataclass(slots=True)
class MarketDataset:
    """Validated dataset crossing the Phase 1 -> Phase 2 boundary."""

    instrument: Instrument
    timeframe: str
    bars: list[MarketBar]
    provenance: DatasetProvenance
    validation: ValidationReport = field(default_factory=ValidationReport)
    normalized: bool = False

    @property
    def start(self) -> datetime | None:
        return self.bars[0].utc_timestamp if self.bars else None

    @property
    def end(self) -> datetime | None:
        return self.bars[-1].utc_timestamp if self.bars else None

    @property
    def research_ready(self) -> bool:
        return bool(self.bars) and self.normalized and self.validation.is_valid

"""Market-data acquisition request."""

from dataclasses import dataclass
from datetime import datetime

from app.market_data.models.instrument import Instrument


@dataclass(frozen=True, slots=True)
class DataRequest:
    instrument: Instrument
    timeframe: str
    start: datetime
    end: datetime

    def __post_init__(self) -> None:
        if self.start.tzinfo is None or self.start.utcoffset() is None:
            raise ValueError("request start must be timezone-aware")
        if self.end.tzinfo is None or self.end.utcoffset() is None:
            raise ValueError("request end must be timezone-aware")
        if self.end < self.start:
            raise ValueError("request end must not precede request start")
        if not self.timeframe.strip():
            raise ValueError("timeframe must not be empty")

"""Canonical OHLCV-style market bar."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from app.market_data.models.instrument import Instrument


@dataclass(frozen=True, slots=True)
class MarketBar:
    """One immutable observation for a fixed instrument and timeframe."""

    instrument: Instrument
    timestamp: datetime
    timeframe: str
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal | None = None
    tick_volume: int | None = None
    bid: Decimal | None = None
    ask: Decimal | None = None
    spread: Decimal | None = None

    def __post_init__(self) -> None:
        if self.timestamp.tzinfo is None or self.timestamp.utcoffset() is None:
            raise ValueError("MarketBar timestamp must be timezone-aware")
        if not self.timeframe.strip():
            raise ValueError("timeframe must not be empty")
        for name in ("open", "high", "low", "close"):
            value = getattr(self, name)
            if not value.is_finite() or value <= 0:
                raise ValueError(f"{name} must be a finite positive Decimal")
        if self.high < max(self.open, self.close) or self.low > min(self.open, self.close):
            raise ValueError("OHLC values are internally inconsistent")
        if self.high < self.low:
            raise ValueError("high must be greater than or equal to low")
        if self.volume is not None and (not self.volume.is_finite() or self.volume < 0):
            raise ValueError("volume must be finite and non-negative")
        if self.tick_volume is not None and self.tick_volume < 0:
            raise ValueError("tick_volume must be non-negative")
        for name in ("bid", "ask", "spread"):
            value = getattr(self, name)
            if value is not None and (not value.is_finite() or value < 0):
                raise ValueError(f"{name} must be finite and non-negative")
        if self.bid is not None and self.ask is not None and self.ask < self.bid:
            raise ValueError("ask must be greater than or equal to bid")

    @property
    def utc_timestamp(self) -> datetime:
        from datetime import timezone

        return self.timestamp.astimezone(timezone.utc)

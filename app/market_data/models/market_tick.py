"""Canonical market tick representation."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from app.market_data.models.instrument import Instrument


@dataclass(frozen=True, slots=True)
class MarketTick:
    instrument: Instrument
    timestamp: datetime
    bid: Decimal
    ask: Decimal

    def __post_init__(self) -> None:
        if self.timestamp.tzinfo is None or self.timestamp.utcoffset() is None:
            raise ValueError("MarketTick timestamp must be timezone-aware")
        if not self.bid.is_finite() or not self.ask.is_finite() or self.bid <= 0 or self.ask <= 0:
            raise ValueError("bid and ask must be finite and positive")
        if self.ask < self.bid:
            raise ValueError("ask must be greater than or equal to bid")

    @property
    def spread(self) -> Decimal:
        return self.ask - self.bid

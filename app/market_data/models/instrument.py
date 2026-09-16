"""Canonical instrument identity and market metadata."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class Instrument:
    """Canonical identity for one tradable market instrument."""

    symbol: str
    asset_class: str = "forex"
    base_currency: str | None = None
    quote_currency: str | None = None
    price_precision: int | None = None
    provider_symbol: str | None = None
    contract_size: Decimal | None = None

    def __post_init__(self) -> None:
        symbol = self.symbol.strip().upper()
        if not symbol:
            raise ValueError("Instrument symbol must not be empty")
        if self.price_precision is not None and self.price_precision < 0:
            raise ValueError("price_precision must be non-negative")
        if self.contract_size is not None and self.contract_size <= 0:
            raise ValueError("contract_size must be positive")
        object.__setattr__(self, "symbol", symbol)
        object.__setattr__(self, "asset_class", self.asset_class.strip().lower())

    @property
    def canonical_id(self) -> str:
        return f"{self.asset_class}:{self.symbol}"

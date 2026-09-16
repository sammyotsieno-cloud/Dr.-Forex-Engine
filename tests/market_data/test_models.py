"""Phase 1 data model tests."""

from datetime import datetime, timezone
from decimal import Decimal

import pytest

from app.market_data.models.instrument import Instrument
from app.market_data.models.market_bar import MarketBar


def test_instrument_has_canonical_identity():
    assert Instrument("eur/usd").canonical_id == "forex:EUR/USD"


def test_market_bar_requires_timezone_aware_timestamp():
    with pytest.raises(ValueError, match="timezone-aware"):
        MarketBar(Instrument("EUR/USD"), datetime(2026, 1, 1), "1h", Decimal("1.1"), Decimal("1.2"), Decimal("1.0"), Decimal("1.15"))


def test_market_bar_rejects_inconsistent_ohlc():
    with pytest.raises(ValueError, match="internally inconsistent"):
        MarketBar(Instrument("EUR/USD"), datetime(2026, 1, 1, tzinfo=timezone.utc), "1h", Decimal("1.1"), Decimal("1.05"), Decimal("1.0"), Decimal("1.15"))

"""Tests for provider routing and reproducible dataset identity."""

from datetime import datetime, timezone

from app.market_data.acquisition.data_request import DataRequest
from app.market_data.acquisition.data_router import DataSourceRegistry
from app.market_data.models.instrument import Instrument
from app.market_data.models.market_dataset import DatasetProvenance
from app.market_data.pipeline.market_data_pipeline import MarketDataPipeline


class Source:
    name = "test-source"

    def __init__(self, supported_symbol: str) -> None:
        self.supported_symbol = supported_symbol

    def supports(self, request: DataRequest) -> bool:
        return request.instrument.symbol == self.supported_symbol

    def fetch(self, request: DataRequest):
        return []


def test_registry_resolves_capable_source():
    registry = DataSourceRegistry()
    source = Source("EUR/USD")
    registry.register(source)
    request = DataRequest(
        Instrument("EUR/USD"),
        "1h",
        datetime(2026, 1, 1, tzinfo=timezone.utc),
        datetime(2026, 1, 2, tzinfo=timezone.utc),
    )
    assert registry.resolve(request) is source


def test_dataset_fingerprint_is_stable_for_same_canonical_data():
    records = [
        {"timestamp": "2026-01-01T00:00:00Z", "open": "1.10", "high": "1.20", "low": "1.00", "close": "1.15"},
        {"timestamp": "2026-01-01T01:00:00Z", "open": "1.15", "high": "1.25", "low": "1.10", "close": "1.20"},
    ]
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    provenance = DatasetProvenance("test-source", start, start.replace(hour=1), start)
    first = MarketDataPipeline().process(records, Instrument("EUR/USD"), "1h", provenance)
    second = MarketDataPipeline().process(records, Instrument("EUR/USD"), "1h", provenance)
    assert first.fingerprint == second.fingerprint

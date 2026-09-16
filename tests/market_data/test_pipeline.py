"""Phase 1 pipeline integrity tests."""

from datetime import datetime, timezone
from decimal import Decimal

import pytest

from app.market_data.models.instrument import Instrument
from app.market_data.models.market_dataset import DatasetProvenance
from app.market_data.pipeline.market_data_pipeline import DataIntegrityError, MarketDataPipeline


def provenance():
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    return DatasetProvenance("test-source", start, start, start)


def valid_records():
    return [
        {"timestamp": "2026-01-01T00:00:00Z", "open": "1.10", "high": "1.20", "low": "1.00", "close": "1.15"},
        {"timestamp": "2026-01-01T01:00:00Z", "open": "1.15", "high": "1.25", "low": "1.10", "close": "1.20"},
    ]


def test_pipeline_returns_research_ready_dataset():
    dataset = MarketDataPipeline().process(valid_records(), Instrument("EUR/USD"), "1h", provenance())
    assert dataset.research_ready
    assert dataset.bars[0].utc_timestamp.tzinfo == timezone.utc
    assert dataset.bars[0].close == Decimal("1.15")


def test_pipeline_rejects_missing_required_field():
    records = valid_records()
    del records[0]["high"]
    with pytest.raises(DataIntegrityError):
        MarketDataPipeline().process(records, Instrument("EUR/USD"), "1h", provenance())


def test_pipeline_rejects_duplicate_timestamp():
    records = valid_records()
    records[1]["timestamp"] = records[0]["timestamp"]
    with pytest.raises(DataIntegrityError):
        MarketDataPipeline().process(records, Instrument("EUR/USD"), "1h", provenance())

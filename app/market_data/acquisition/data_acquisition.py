"""Acquisition boundary preserving provider observations."""

from app.market_data.acquisition.data_request import DataRequest
from app.market_data.acquisition.data_source import MarketDataSource


class DataAcquisition:
    def acquire(self, source: MarketDataSource, request: DataRequest) -> list[dict]:
        records = list(source.fetch(request))
        if not records:
            return []
        return records

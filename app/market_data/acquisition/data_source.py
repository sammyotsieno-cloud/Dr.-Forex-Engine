"""Provider adapter protocol."""

from collections.abc import Iterable
from typing import Protocol

from app.market_data.acquisition.data_request import DataRequest


class MarketDataSource(Protocol):
    name: str

    def fetch(self, request: DataRequest) -> Iterable[dict]:
        """Return raw observations; validation belongs to later stages."""

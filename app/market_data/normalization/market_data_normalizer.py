"""Provider-independent canonicalization."""

from decimal import Decimal

from app.market_data.models.instrument import Instrument
from app.market_data.models.market_bar import MarketBar
from app.market_data.normalization.timestamp_normalizer import TimestampNormalizer


class MarketDataNormalizer:
    def normalize(self, records: list[dict], instrument: Instrument, timeframe: str) -> list[MarketBar]:
        bars: list[MarketBar] = []
        for index, record in enumerate(records):
            try:
                bars.append(MarketBar(
                    instrument=instrument,
                    timestamp=TimestampNormalizer.normalize(record["timestamp"]),
                    timeframe=timeframe.strip().lower(),
                    open=Decimal(str(record["open"])),
                    high=Decimal(str(record["high"])),
                    low=Decimal(str(record["low"])),
                    close=Decimal(str(record["close"])),
                    volume=self._decimal(record.get("volume")),
                    tick_volume=self._int(record.get("tick_volume")),
                    bid=self._decimal(record.get("bid")),
                    ask=self._decimal(record.get("ask")),
                    spread=self._decimal(record.get("spread")),
                ))
            except (KeyError, TypeError, ValueError, ArithmeticError) as exc:
                raise ValueError(f"Record {index} cannot be safely normalized: {exc}") from exc
        return bars

    @staticmethod
    def _decimal(value):
        return None if value is None else Decimal(str(value))

    @staticmethod
    def _int(value):
        return None if value is None else int(value)

"""MetaTrader 5 acquisition adapter for user-selected broker connections.

The adapter keeps MT5/provider concerns at the acquisition boundary. Raw
provider observations are passed downstream unchanged; Phase 1 validation
remains responsible for deciding whether data is safe for research.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from app.market_data.acquisition.data_request import DataRequest
from app.market_data.acquisition.data_source import MarketDataSource


@dataclass(frozen=True, slots=True)
class MT5Capabilities:
    """Capabilities discovered from the currently connected MT5 environment."""

    broker: str | None
    server: str | None
    terminal: str | None
    available_symbols: tuple[str, ...]
    supported_timeframes: tuple[str, ...]

    def supports(self, request: DataRequest) -> bool:
        symbol = request.instrument.provider_symbol or request.instrument.symbol
        return (
            symbol.upper() in {item.upper() for item in self.available_symbols}
            and request.timeframe in self.supported_timeframes
        )


class MT5Connection:
    """Reusable connection boundary around the MetaTrader 5 terminal.

    Credentials are supplied only to the terminal connection call and are never
    retained by this object. Connection does not grant trading authority.
    """

    _TIMEFRAMES = {
        "1m": "TIMEFRAME_M1",
        "5m": "TIMEFRAME_M5",
        "15m": "TIMEFRAME_M15",
        "30m": "TIMEFRAME_M30",
        "1h": "TIMEFRAME_H1",
        "4h": "TIMEFRAME_H4",
        "1d": "TIMEFRAME_D1",
    }

    def __init__(self, client: Any | None = None) -> None:
        self._client = client
        self._connected = False

    @property
    def connected(self) -> bool:
        return self._connected

    def connect(
        self,
        *,
        path: str | None = None,
        login: int | None = None,
        password: str | None = None,
        server: str | None = None,
        timeout: int = 60_000,
        portable: bool = False,
    ) -> None:
        client = self._load_client()
        kwargs: dict[str, Any] = {"timeout": timeout, "portable": portable}
        if login is not None:
            kwargs["login"] = login
        if password is not None:
            kwargs["password"] = password
        if server is not None:
            kwargs["server"] = server
        if path is not None:
            kwargs["path"] = path
        if not client.initialize(**kwargs):
            code, message = client.last_error()
            raise ConnectionError(f"MT5 initialization failed ({code}): {message}")
        self._connected = True

    def disconnect(self) -> None:
        if self._client is not None and self._connected:
            self._client.shutdown()
        self._connected = False

    def capabilities(self) -> MT5Capabilities:
        self._require_connection()
        terminal = self._client.terminal_info()
        account = self._client.account_info()
        symbols = self._client.symbols_get()
        if symbols is None:
            code, message = self._client.last_error()
            raise RuntimeError(f"MT5 symbol discovery failed ({code}): {message}")
        return MT5Capabilities(
            broker=getattr(account, "company", None) if account else None,
            server=getattr(account, "server", None) if account else None,
            terminal=getattr(terminal, "name", None) if terminal else None,
            available_symbols=tuple(
                item.name for item in symbols if getattr(item, "name", "")
            ),
            supported_timeframes=tuple(self._TIMEFRAMES),
        )

    def timeframe_constant(self, timeframe: str) -> Any:
        self._require_connection()
        constant_name = self._TIMEFRAMES.get(timeframe)
        if constant_name is None:
            raise ValueError(f"Unsupported MT5 timeframe: {timeframe}")
        return getattr(self._client, constant_name)

    def _require_connection(self) -> None:
        if not self._connected or self._client is None:
            raise ConnectionError("MT5 terminal is not connected")

    def _load_client(self) -> Any:
        if self._client is None:
            try:
                import MetaTrader5 as client
            except ImportError as exc:
                raise RuntimeError(
                    "MetaTrader5 is not installed. Install the optional 'mt5' dependency."
                ) from exc
            self._client = client
        return self._client


class MT5DataSource(MarketDataSource):
    """MarketDataSource implementation backed by a connected MT5 terminal."""

    name = "MetaTrader 5"

    def __init__(self, connection: MT5Connection) -> None:
        self.connection = connection

    @property
    def broker(self) -> str | None:
        return self.connection.capabilities().broker

    @property
    def server(self) -> str | None:
        return self.connection.capabilities().server

    @property
    def source_reference(self) -> str:
        return "MT5 terminal / broker server"

    def fetch(self, request: DataRequest) -> list[dict[str, Any]]:
        self.connection._require_connection()
        capabilities = self.connection.capabilities()
        symbol = request.instrument.provider_symbol or request.instrument.symbol
        if not capabilities.supports(request):
            raise ValueError(
                f"MT5 cannot satisfy request for symbol={symbol}, timeframe={request.timeframe}"
            )
        timeframe = self.connection.timeframe_constant(request.timeframe)
        start = request.start.astimezone(timezone.utc)
        end = request.end.astimezone(timezone.utc)
        if not self.connection._client.symbol_select(symbol, True):
            code, message = self.connection._client.last_error()
            raise RuntimeError(f"MT5 symbol selection failed ({code}): {message}")
        rates = self.connection._client.copy_rates_range(symbol, timeframe, start, end)
        if rates is None:
            code, message = self.connection._client.last_error()
            raise RuntimeError(f"MT5 historical data request failed ({code}): {message}")
        return [self._to_raw_record(row) for row in rates]

    @staticmethod
    def _to_raw_record(row: Any) -> dict[str, Any]:
        timestamp = row["time"]
        if isinstance(timestamp, (int, float)):
            timestamp = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        return {
            "timestamp": timestamp,
            "open": row["open"],
            "high": row["high"],
            "low": row["low"],
            "close": row["close"],
            "tick_volume": int(row["tick_volume"]),
            "volume": int(row["real_volume"]),
            "provider_spread_points": int(row["spread"]),
        }

"""Provider-neutral market-data source registry and capability routing."""

from collections.abc import Callable

from app.market_data.acquisition.data_request import DataRequest
from app.market_data.acquisition.data_source import MarketDataSource


SourcePredicate = Callable[[MarketDataSource, DataRequest], bool]


class DataSourceRegistry:
    """Resolve a research request to an explicitly registered data source.

    Provider-specific rules stay at the adapter boundary. The engine therefore
    does not grow hard-coded ``if provider == ...`` branches as new sources are
    added. A predicate may be supplied for adapters whose capabilities require
    an external discovery step.
    """

    def __init__(self) -> None:
        self._sources: list[tuple[MarketDataSource, SourcePredicate | None]] = []

    def register(
        self,
        source: MarketDataSource,
        *,
        predicate: SourcePredicate | None = None,
    ) -> None:
        if any(existing is source for existing, _ in self._sources):
            raise ValueError("data source is already registered")
        self._sources.append((source, predicate))

    def resolve(self, request: DataRequest) -> MarketDataSource:
        for source, predicate in self._sources:
            if predicate is not None:
                if predicate(source, request):
                    return source
                continue
            supports = getattr(source, "supports", None)
            if supports is None or supports(request):
                return source
        raise LookupError(
            "No registered market-data source can satisfy "
            f"{request.instrument.symbol} {request.timeframe}"
        )

    def sources(self) -> tuple[MarketDataSource, ...]:
        """Return registered sources without exposing mutable registry state."""
        return tuple(source for source, _ in self._sources)

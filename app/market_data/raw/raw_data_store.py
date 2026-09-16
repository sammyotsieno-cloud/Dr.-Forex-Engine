"""Raw observation preservation boundary."""

from copy import deepcopy


class RawDataStore:
    def __init__(self) -> None:
        self._records: list[dict] = []

    def append(self, records: list[dict]) -> None:
        self._records.extend(deepcopy(records))

    def read(self) -> list[dict]:
        return deepcopy(self._records)

    def clear(self) -> None:
        self._records.clear()

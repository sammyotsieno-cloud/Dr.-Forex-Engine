"""Canonical UTC timestamp normalization."""

from datetime import datetime, timezone


class TimestampNormalizer:
    @staticmethod
    def normalize(value: datetime | str) -> datetime:
        if isinstance(value, str):
            text = value.strip()
            if text.endswith("Z"):
                text = text[:-1] + "+00:00"
            value = datetime.fromisoformat(text)
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Timestamp has no timezone; refusing to infer one")
        return value.astimezone(timezone.utc)

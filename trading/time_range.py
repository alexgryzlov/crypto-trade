from __future__ import annotations
from trading import Timestamp


class TimeRange:
    def __init__(self, from_ts: int, to_ts: int):
        self.from_ts = from_ts
        self.to_ts = to_ts

    def __str__(self) -> str:
        return self.to_iso_format()

    def get_range(self) -> int:
        return self.to_ts - self.from_ts

    def to_iso_format(self) -> str:
        return f'{Timestamp.to_iso_format(self.from_ts)}-{Timestamp.to_iso_format(self.to_ts)}'

    @classmethod
    def from_iso_format(cls, from_ts: str, to_ts: str) -> TimeRange:
        return cls(
            from_ts=Timestamp.from_iso_format(from_ts),
            to_ts=Timestamp.from_iso_format(to_ts))

from dateutil import parser

from trading import Timestamp


class TimeRange:
    def __init__(self, from_ts: int, to_ts: int):
        self.from_ts = from_ts
        self.to_ts = to_ts

    def __str__(self):
        return self.to_iso_format()

    def get_range(self):
        return self.to_ts - self.from_ts

    def to_iso_format(self):
        return f'{Timestamp.to_iso_format(self.from_ts)}-{Timestamp.to_iso_format(self.to_ts)}'

    @classmethod
    def from_iso_format(cls, from_ts: str, to_ts: str):
        return TimeRange(
            from_ts=int(parser.parse(from_ts).timestamp()),
            to_ts=int(parser.parse(to_ts).timestamp()))

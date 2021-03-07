from dateutil import parser


class TimeRange:
    def __init__(self, from_ts: int, to_ts: int):
        self.from_ts: int = from_ts
        self.to_ts: int = to_ts

    @classmethod
    def from_iso_format(cls, from_ts: str, to_ts: str):
        return TimeRange(
            from_ts=int(parser.parse(from_ts).timestamp()),
            to_ts=int(parser.parse(to_ts).timestamp()))

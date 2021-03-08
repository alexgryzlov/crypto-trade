from datetime import datetime
from dateutil import parser


class Timestamp:
    @staticmethod
    def to_iso_format(ts: int) -> str:
        return str(datetime.fromtimestamp(ts))

    @staticmethod
    def from_iso_format(ts: str) -> int:
        return int(parser.parse(ts).timestamp())

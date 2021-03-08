from datetime import datetime


class Timestamp:
    @classmethod
    def to_iso_format(cls, ts: int):
        return datetime.fromtimestamp(ts)

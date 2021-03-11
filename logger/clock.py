from datetime import datetime


class Clock:
    def __init__(self) -> None:
        pass

    def get_timestamp(self) -> int:
        return int(datetime.now().timestamp())

from datetime import datetime


class Clock:
    def __init__(self):
        pass

    def get_timestamp(self):
        return int(datetime.now().timestamp())

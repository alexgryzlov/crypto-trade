_base_to_seconds = {
    'm': 60,
    'h': 60 * 60,
    'd': 60 * 60 * 24,
    'w': 60 * 60 * 24 * 7,
}


class Timeframe:
    def __init__(self, timeframe: str):
        self.timeframe = timeframe
        self.value = int(timeframe[:-1])
        self.base = timeframe[-1]

    def __str__(self):
        return self.timeframe

    def __int__(self):
        return self.to_seconds()

    def __repr__(self):
        return f'Timeframe: {self.timeframe}'

    def to_seconds(self):
        return _base_to_seconds[self.base] * self.value

    def to_string(self):
        return self.timeframe

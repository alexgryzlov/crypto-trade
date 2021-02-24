from enum import Enum, auto


class TrendType(Enum):
    UPTREND = auto()
    DOWNTREND = auto()


class TrendLine:
    """Trend line of the form y(x) = kx + b"""

    def __init__(self, k, b):
        self.k = k
        self.b = b

    def get_value_at(self, x):
        return self.k * x + self.b


class Trend:
    def __init__(self, trend_type, lower_trend_line=None, upper_trend_line=None):
        self.trend_type = trend_type
        self.lower_trend_line = lower_trend_line
        self.upper_trend_line = upper_trend_line

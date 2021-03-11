from enum import Enum, auto
import numpy as np
import typing as tp


class TrendType(Enum):
    UPTREND = auto()
    DOWNTREND = auto()


class TrendLine:
    """Trend line of the form y(x) = kx + b"""

    def __init__(self, k: float, b: float):
        self.k = k
        self.b = b

    def get_value_at(self, x: tp.Union[float, np.ndarray]) -> float:
        return self.k * x + self.b


class Trend:
    def __init__(self, trend_type: TrendType,
                 lower_trend_line: tp.Union[TrendLine, None] = None,
                 upper_trend_line: tp.Union[TrendLine, None] = None):
        self.trend_type = trend_type
        self.lower_trend_line = lower_trend_line
        self.upper_trend_line = upper_trend_line

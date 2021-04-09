from enum import Enum, auto


class RsiSignalType(Enum):
    OVERSOLD = auto()
    OVERBOUGHT = auto()


class RsiSignal:
    def __init__(self, rsi_type: RsiSignalType, value: float):
        self.type = rsi_type
        self.value = value

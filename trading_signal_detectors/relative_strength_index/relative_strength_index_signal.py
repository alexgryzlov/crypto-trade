from enum import Enum, auto


class RSISignalType(Enum):
    OVERSOLD = auto()
    OVERBOUGHT = auto()


class RSISignal:
    def __init__(self, rsi_type: RSISignalType, value: float):
        self.type = rsi_type
        self.value = value

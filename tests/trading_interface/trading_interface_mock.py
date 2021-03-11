from trading import Candle
from trading_interface.trading_interface import TradingInterface


class TradingInterfaceMock(TradingInterface):
    def __init__(self, all_candles=[]):
        self.all_candles = all_candles
        self.processed_candles = []

    @classmethod
    def from_price_values(cls, values):
        candles = []
        for i in range(len(values) - 1):
            candles.append(Candle(
                ts=i,
                open=values[i],
                close=values[i + 1],
                low=min(values[i], values[i + 1]),
                high=max(values[i], values[i + 1]),
                volume=1)
            )
        return cls(candles)

    def refresh(self):
        self.processed_candles = []

    def update(self) -> bool:
        if len(self.processed_candles) < len(self.all_candles):
            self.processed_candles.append(self.all_candles[len(self.processed_candles)])
            return True
        return False

    def is_alive(self):
        return len(self.processed_candles) < len(self.all_candles)

    def get_timestamp(self):
        return len(self.processed_candles)

    def get_last_n_candles(self, n: int):
        return self.processed_candles[-n:]

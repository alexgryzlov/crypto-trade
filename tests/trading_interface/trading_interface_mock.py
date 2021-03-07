from trading.asset import AssetPair
from trading.candle import Candle
from trading.order import Order
from trading_interface.trading_interface import TradingInterface


class TradingInterfaceMock(TradingInterface):
    def __init__(self, all_candles=None):
        if all_candles:
            self.all_candles = all_candles
        else:
            self.all_candles = []
        self.candles = []

    @classmethod
    def from_price_values(cls, values):
        candles = []
        for i in range(len(values) - 1):
            candles.append(Candle(
                i,
                values[i],
                values[i + 1],
                min(values[i], values[i + 1]),
                max(values[i], values[i + 1]))
            )
        return cls(candles)

    def refresh(self):
        self.candles = []

    def update(self) -> bool:
        if len(self.candles) < len(self.all_candles):
            self.candles.append(self.all_candles[len(self.candles)])
            return True
        return False

    def is_alive(self):
        return len(self.candles) < len(self.all_candles)

    def get_timestamp(self):
        return len(self.candles)

    def get_last_n_candles(self, n: int):
        return self.candles[-n:]

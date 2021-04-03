from trading_system.trading_system_handler import TradingSystemHandler
from trading_interface.trading_interface import TradingInterface
from trading.candle import Candle

import typing as tp


class VolumeRelativeStrengthIndexHandler(TradingSystemHandler):
    """
         Volume Relative Strength Index formula:
         VRSI = 100 - 100 / (1 + VORS), where
         VORS = (Average Up-Volume) / (Average Down-Volume)
     """

    def __init__(self, trading_interface: TradingInterface, window_size: int = 14) -> None:
        super().__init__(trading_interface)
        self.ti = trading_interface

        self.window_size = window_size

        self.values: tp.List[float] = []

    def update(self) -> bool:
        if not super().received_new_candle():
            return False

        candles = self.ti.get_last_n_candles(self.window_size)
        if len(candles) < self.window_size:
            return False
        self.values.append(self.calculate_from(candles, self.window_size)[0])
        return True

    def get_last_n_values(self, n: int) -> tp.List[float]:
        return self.values[-n:]

    @staticmethod
    def calculate_from(candles: tp.List[Candle], window_size: int) -> tp.List[float]:
        vrsi_values: tp.List[float] = []
        for i in range(window_size, len(candles) + 1):
            total_volume = sum([candle.volume for candle in candles[i - window_size:i]])
            up_volume = sum([candle.volume if candle.get_delta() >= 0 else 0 for candle in candles[i - window_size:i]])
            vrsi_values.append(100 * up_volume / total_volume)
        return vrsi_values

from trading_system.trading_system_handler import TradingSystemHandler
from trading_interface.trading_interface import TradingInterface


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

        self.values = []

    def update(self) -> None:
        if not super().received_new_candle():
            return

        candles = self.ti.get_last_n_candles(self.window_size)
        if len(candles) < self.window_size:
            return

        up_volume = sum([candle.volume if candle.get_delta >= 0 else 0 for candle in candles])
        down_volume = sum([-candle.volume if candle.get_delta < 0 else 0 for candle in candles])
        self.values.append(100 - 100 / (1 + up_volume / down_volume))

    def get_last_n_values(self, n) -> list:
        return self.values[-n:]

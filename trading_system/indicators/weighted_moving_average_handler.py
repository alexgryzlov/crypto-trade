from trading_system.trading_system_handler import TradingSystemHandler
from trading_interface.trading_interface import TradingInterface

import numpy as np

import typing as tp


class WeightedMovingAverageHandler(TradingSystemHandler):
    """ Weighted Moving Average (WMA) """

    def __init__(self, trading_interface: TradingInterface, window_size: int):
        super().__init__(trading_interface)
        self.ti = trading_interface

        self.window_size = window_size
        self.weights = np.arange(1, window_size + 1)
        self.denominator = window_size * (window_size + 1) // 2

        self.values: tp.List[float] = []

    def get_name(self) -> str:
        return f'{type(self).__name__}{self.window_size}'

    def update(self) -> None:
        if not super().received_new_candle():
            return

        candles = self.ti.get_last_n_candles(self.window_size)
        if len(candles) < self.window_size:
            return

        candle_values = list(map(lambda c: c.get_mid_price(), candles))
        self.values.append(
            np.sum(self.weights * candle_values) / self.denominator)

    def get_last_n_values(self, n: int) -> tp.List[float]:
        return self.values[-n:]

    @staticmethod
    def calculate_from(values: tp.List[float]) -> float:
        coefs = np.arange(1, len(values) + 1)
        return np.sum(coefs * values) / (len(values) * (len(values) + 1) / 2)

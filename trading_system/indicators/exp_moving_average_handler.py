from trading_system.trading_system_handler import TradingSystemHandler
from trading_interface.trading_interface import TradingInterface
from logger.logger import Logger
from logger.log_events import ExpMovingAverageEvent

import numpy as np

import typing as tp
from helpers.typing import Array


class ExpMovingAverageHandler(TradingSystemHandler):
    """ Exponential Moving Average (EMA) """

    def __init__(self, trading_interface: TradingInterface, window_size: int,
                 smoothing: float = 2):
        super().__init__(trading_interface)
        self.ti = trading_interface

        self.window_size = window_size
        self.smoothing = smoothing
        self.alpha = smoothing / (1 + window_size)

        self.values: tp.List[float] = []
        self.logger = Logger(self.get_name())

    def get_name(self) -> str:
        return f'{type(self).__name__}{self.window_size}_{self.smoothing}'

    def update(self) -> bool:
        if not super().received_new_candle():
            return False

        new_candle = self.ti.get_last_n_candles(1)[0]
        if len(self.values) > 0:
            self.values.append(
                new_candle.get_mid_price() * self.alpha +
                self.values[-1] * (1 - self.alpha))
        else:
            self.values.append(new_candle.get_mid_price())
        self.logger.trading(
            ExpMovingAverageEvent(self.values[-1], self.window_size))
        return True

    def get_last_n_values(self, n: int) -> tp.List[float]:
        return self.values[-n:]

    @staticmethod
    def calculate_from(values: Array[float],
                       alpha: tp.Optional[float] = None) -> float:
        if alpha is None:
            alpha = 2 / (1 + len(values))

        coefs = np.logspace(len(values) - 1, 0, num=len(values),
                            base=1 - alpha)
        coefs[0] /= alpha
        return alpha * np.sum(coefs * values)

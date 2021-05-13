import typing as tp
from logging import INFO

from helpers.typing import Array
from logger.log_events import MovingAverageEvent
from logger.logger import Logger
from trading_interface.trading_interface import TradingInterface
from trading_system.trading_system_handler import TradingSystemHandler


class MovingAverageHandler(TradingSystemHandler):
    """ Simple Moving Average (SMA or MA) """

    def __init__(self, trading_interface: TradingInterface, window_size: int):
        super().__init__(trading_interface)
        self.ti = trading_interface

        self.window_size = window_size

        self.values: tp.List[float] = []
        self.logger = Logger(self.get_name())

    def get_name(self) -> str:
        return f'{type(self).__name__}{self.window_size}'

    def update(self) -> bool:
        if not super().received_new_candle():
            return False

        candles = self.ti.get_last_n_candles(self.window_size)
        if len(candles) < self.window_size:
            return False

        candle_values = list(map(lambda c: c.get_mid_price(), candles))
        self.values.append(self.calculate_from(candle_values))
        self.logger.info_event(
            MovingAverageEvent(self.get_last_n_values(1)[0], self.window_size))
        return True

    def get_last_n_values(self, n: int) -> tp.List[float]:
        return self.values[-n:]

    @staticmethod
    def calculate_from(values: Array[float]) -> float:
        return sum(values) / len(values)

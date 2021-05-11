import typing as tp
import numpy as np

import trading_system.trading_system as ts
from logger.logger import Logger

from trading_system.indicators import MovingAverageHandler
from trading_signal_detectors.trading_signal_detector import TradingSignalDetector
from trading import Signal, TrendType

PRICE_EPS = 0.05


class MovingAverageSignalDetector(TradingSignalDetector):
    def __init__(self, trading_system: ts.TradingSystem,
                 k_nearest: int, k_further: int, signal_length: int = 5):
        self.logger = Logger('MovingAverageSignalDetector')
        self.ts = trading_system
        self.signal_length = signal_length
        self.nearest_handler: MovingAverageHandler = \
            self.ts.add_handler(MovingAverageHandler,
                                params={"window_size": k_nearest})
        self.further_handler: MovingAverageHandler = \
            self.ts.add_handler(MovingAverageHandler,
                                params={"window_size": k_further})

    def get_trading_signals(self) -> tp.List[Signal]:
        further_values = self.further_handler.get_last_n_values(
            self.signal_length)
        nearest_values = self.nearest_handler.get_last_n_values(
            self.signal_length)

        if len(further_values) < self.signal_length:
            return []
        values = np.array(nearest_values) - np.array(further_values)

        if values[0] < -PRICE_EPS and values[-1] > PRICE_EPS and \
                self.__is_increasing(values):
            return [Signal("moving_average", TrendType.UPTREND)]

        if values[0] > -PRICE_EPS and values[-1] < PRICE_EPS and \
                self.__is_decreasing(values):
            return [Signal("moving_average", TrendType.DOWNTREND)]

        return []

    def __is_increasing(self, arr: tp.List[float]) -> bool:
        for i in range(len(arr) - 1):
            if arr[i] > arr[i + 1]:
                return False
        return True

    def __is_decreasing(self, arr: tp.List[float]) -> bool:
        return self.__is_increasing(list(reversed(arr)))

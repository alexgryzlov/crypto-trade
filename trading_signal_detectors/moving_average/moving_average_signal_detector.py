import numpy as np

from trading_signal_detectors.trading_signal_detector import TradingSignalDetector
from trading_system.moving_average_handler import MovingAverageHandler
from trading import Signal, TrendType

from logger import logger

PRICE_EPS = 0.05


class MovingAverageSignalDetector(TradingSignalDetector):
    def __init__(self, trading_system, k_nearest, k_further, signal_length=5):
        self.logger = logger.get_logger('MovingAverageSignalDetector')
        self.ts = trading_system
        self.signal_length = signal_length
        self.nearest_handler: MovingAverageHandler = \
            trading_system.handlers[f'MovingAverageHandler{k_nearest}']
        self.further_handler: MovingAverageHandler = \
            trading_system.handlers[f'MovingAverageHandler{k_further}']

    def get_trading_signals(self):
        further_values = self.further_handler.get_n_average_values(self.signal_length)
        nearest_values = self.nearest_handler.get_n_average_values(self.signal_length)

        if len(further_values) < self.signal_length:
            return []
        values = np.array(nearest_values) - np.array(further_values)

        if values[0] < -PRICE_EPS and values[-1] > PRICE_EPS and self.__is_increasing(values):
            return [Signal("moving_average", TrendType.UPTREND)]

        if values[0] > -PRICE_EPS and values[-1] < PRICE_EPS and self.__is_decreasing(values):
            return [Signal("moving_average", TrendType.DOWNTREND)]

        return []

    def __is_increasing(self, arr):
        for i in range(len(arr) - 1):
            if arr[i] > arr[i + 1]:
                return False
        return True

    def __is_decreasing(self, arr):
        return self.__is_increasing(list(reversed(arr)))

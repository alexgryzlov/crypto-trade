from trading_signal_detectors.trading_signal_detector import TradingSignalDetector
from trading.signal import Signal
from logger import logger
from trading.trend import TrendType

PRICE_SHIFT = 0.005


class ExtremumSignalDetector(TradingSignalDetector):
    def __init__(self, trading_system, extremum_count):
        self.logger = logger.get_logger('ExtremumSignalDetector')
        self.ts = trading_system
        self.extremum_count = extremum_count
        self.local_maximums = []
        self.local_minimums = []
        self.last_candle_timestamp = -1

    def get_trading_signals(self):
        self.__update()

        if len(self.local_minimums) >= self.extremum_count and \
                len(self.local_maximums) >= self.extremum_count:

            if self.__is_increasing(self.local_maximums[-self.extremum_count:]) and \
                    self.__is_increasing(self.local_minimums[-self.extremum_count:]):
                self.logger.info("Extremum uptrend detected")
                return [Signal("extremum", TrendType.UPTREND)]

            if self.__is_decreasing(self.local_maximums[-self.extremum_count:]) and \
                    self.__is_decreasing(self.local_minimums[-self.extremum_count:]):
                self.logger.info("Extremum downtrend detected")
                return [Signal("extremum", TrendType.DOWNTREND)]

        return []

    def __update(self):
        candles = self.ts.get_last_n_candles(3)
        if len(candles) < 3:
            return

        if self.last_candle_timestamp == candles[-1].ts:
            return
        self.last_candle_timestamp = candles[-1].ts

        if self.__is_local_maximum(*[c.get_upper_price() for c in candles]):
            self.local_maximums.append(candles[-2].get_upper_price())

        if self.__is_local_minimum(*[c.get_lower_price() for c in candles]):
            self.local_minimums.append(candles[-2].get_lower_price())

    def __is_increasing(self, arr):
        for i in range(len(arr) - 1):
            if arr[i] * (1 + PRICE_SHIFT) > arr[i + 1]:
                return False
        return True

    def __is_decreasing(self, arr):
        return self.__is_increasing(list(reversed(arr)))

    def __is_local_maximum(self, left_candle, middle_candle, right_candle):
        return max(left_candle, right_candle) * (1 + PRICE_SHIFT) < middle_candle

    def __is_local_minimum(self, left_candle, middle_candle, right_candle):
        return min(left_candle, right_candle) * (1 - PRICE_SHIFT) > middle_candle

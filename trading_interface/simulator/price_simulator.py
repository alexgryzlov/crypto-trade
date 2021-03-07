import numpy as np

from trading.candle import Candle
from logger import logger


class PriceSimulator:
    """
    Simulates price changes within single candle.
    Depending on the parity of timestamp hash chooses between:
        1. open -> high -> low -> close
        2. open -> low -> high -> close
    Noise can be optionally added
    """

    def __init__(self, candles_lifetime, simulation_type):
        self.candles_lifetime = candles_lifetime
        self.current_ts = None
        self.prices = [0] * candles_lifetime
        self.noise = np.random.normal
        self.simulation_type = simulation_type
        self.logger = logger.get_logger('PriceSimulator')

    def get_price(self, candle: Candle, current_lifetime):
        if candle.ts != self.current_ts:
            self.current_ts = candle.ts
            try:
                self.prices = self.__getattribute__(self.simulation_type)(candle)
            except AttributeError:
                self.logger.exception('Unknown PriceSimulator type.')
        return self.prices[current_lifetime]

    def three_interval_path(self, candle):
        return self._high_to_low(candle) if hash(str(candle.ts)) % 2 == 0 else self._low_to_high(candle)

    def three_interval_path_noise(self, candle):
        self.noise = lambda: np.random.normal(0, (candle.high - candle.low) / self.candles_lifetime)
        return self._high_to_low(candle, True) if hash(str(candle.ts)) % 2 == 0 else self._low_to_high(candle, True)

    def _uniform(self, candle: Candle):
        return [candle.get_delta() * (i / self.candles_lifetime) + candle.open for i in range(self.candles_lifetime)]

    def _high_to_low(self, candle: Candle, noise=False):
        path = [[candle.open, candle.high], [candle.high, candle.low], [candle.low, candle.close]]
        return self._multi_interval_path(path, self.candles_lifetime, noise)

    def _low_to_high(self, candle: Candle, noise=False):
        path = [[candle.open, candle.low], [candle.low, candle.high], [candle.high, candle.close]]
        return self._multi_interval_path(path, self.candles_lifetime, noise)

    def _multi_interval_path(self, intervals, total_steps, noise=False):
        """
        returns 'total_steps' evenly distributed points on the way described by 'intervals'
        starts and ends of intervals are always among the resulting points

        intervals: consecutive intervals [[start_1, end_1], [start_2, end_2] ...]
                   end_i == start_{i+1}
        """
        if total_steps < len(intervals) + 1:
            self.logger.error("Not enough steps to cover given path.")
            total_steps = len(intervals) + 1

        total_path = 0
        for interval in intervals:
            total_path += abs(interval[1] - interval[0])

        if total_path == 0:
            return intervals[0][0] * total_steps

        prices = []
        # Make sure at least 2 points (start and end) from first interval are in the result
        prices += list(np.linspace(intervals[0][0], intervals[0][1], int(abs(intervals[0][1] - intervals[0][0])
                                                         / total_path * (total_steps - len(intervals) - 1)) + 2))

        # For every intermediate interval don't count its start
        for interval in intervals[1:len(intervals) - 1]:
            prices += list(np.linspace(interval[0], interval[1], int(abs(interval[1] - interval[0]) / total_path *
                                                                     (total_steps - len(intervals) - 1)) + 2)[1:])

        # If int() cut down some points add them in the last interval
        prices += list(np.linspace(intervals[-1][0], intervals[-1][1], total_steps - len(prices) + 1))[1:]

        # Noise doesn't affect starts and ends of the intervals
        if noise:
            low = min([min(i) for i in intervals])
            high = max([max(i) for i in intervals])
            for ind in filter(lambda x: not any(prices[x] in i for i in intervals), range(len(prices))):
                prices[ind] = min(max(prices[ind] + self.noise(), low), high)
        return prices


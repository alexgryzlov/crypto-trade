import numpy as np

from trading import Candle
from logger.logger import Logger


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
        self.simulation_type = simulation_type
        self.logger = Logger('PriceSimulator')

    def get_price(self, candle: Candle, current_lifetime):
        if candle.ts != self.current_ts:
            self.current_ts = candle.ts
            try:
                self.prices = self.__getattribute__(self.simulation_type)(candle)
            except AttributeError as exception:
                self.logger.exception('Unknown PriceSimulator type.')
                raise exception
        return self.prices[current_lifetime]

    def three_interval_path(self, candle):
        return self._high_to_low(candle) if hash(str(candle.ts)) % 2 == 0 else self._low_to_high(candle)

    def three_interval_path_noise(self, candle):
        def noise():
            return np.random.normal(0, (candle.high - candle.low) / self.candles_lifetime)
        np.random.seed(hash(str(candle.ts)))
        return self._high_to_low(candle, noise) if hash(str(candle.ts)) % 2 == 0 else self._low_to_high(candle, noise)

    def uniform(self, candle: Candle):
        return [candle.get_delta() * (i / self.candles_lifetime) + candle.open for i in range(self.candles_lifetime)]

    def _high_to_low(self, candle: Candle, noise=None):
        path = [[candle.open, candle.high], [candle.high, candle.low], [candle.low, candle.close]]
        return self._build_multi_interval_path(path, self.candles_lifetime, noise)

    def _low_to_high(self, candle: Candle, noise=None):
        path = [[candle.open, candle.low], [candle.low, candle.high], [candle.high, candle.close]]
        return self._build_multi_interval_path(path, self.candles_lifetime, noise)

    def _build_multi_interval_path(self, intervals, total_steps, noise=None):
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

        def points_count(interval):
            total_intermediate_points = total_steps - len(intervals) - 1
            relative_length = abs(interval[1] - interval[0]) / total_path
            corner_points = 2
            return int(relative_length * total_intermediate_points) + corner_points

        # Make sure at least 2 points (start and end) from first interval are in the result
        prices += list(np.linspace(intervals[0][0], intervals[0][1], points_count(intervals[0])))

        # For every intermediate interval don't count its start
        for interval in intervals[1:len(intervals) - 1]:
            prices += list(np.linspace(interval[0], interval[1], points_count(interval))[1:])

        # If int() cut down some points add them in the last interval
        prices += list(np.linspace(intervals[-1][0], intervals[-1][1], total_steps - len(prices) + 1))[1:]

        # Noise doesn't affect starts and ends of the intervals
        if noise:
            low = min([min(i) for i in intervals])
            high = max([max(i) for i in intervals])
            for ind in filter(lambda x: not any(prices[x] in i for i in intervals), range(len(prices))):
                prices[ind] = min(max(prices[ind] + noise(), low), high)
        return prices


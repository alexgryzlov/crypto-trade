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
    def __init__(self, candles_lifetime, type):
        self.candles_lifetime = candles_lifetime
        self.current_ts = None
        self.prices = [0] * candles_lifetime
        self.noise = np.random.normal
        self.type = type
        self.logger = logger.get_logger('PriceSimulator')

    def get_price(self, candle: Candle, current_lifetime):
        if candle.ts != self.current_ts:
            self.current_ts = candle.ts
            try:
                self.prices = self.__getattribute__(self.type)(candle)
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
        return self.__three_interval_path(candle.open, candle.high, candle.low, candle.close, self.candles_lifetime, noise)

    def _low_to_high(self, candle: Candle, noise=False):
        return self.__three_interval_path(candle.open, candle.low, candle.high, candle.close, self.candles_lifetime, noise)

    def __three_interval_path(self, one, two, three, four, total_steps, noise=False):
        """
        returns 'total_steps' evenly distributed points on the way one -> two -> three -> four
        one, two, three, four are always among the result
        """
        total_path = abs(one - two) + abs(two - three) + abs(three - four)
        first_segment_steps = int((abs(one - two)) / total_path * (total_steps - 4)) + 2
        second_segment_steps = int(abs(two - three) / total_path * (total_steps - 4)) + 1
        third_segment_steps = total_steps - (first_segment_steps + second_segment_steps)
        prices = list(np.linspace(one, two, first_segment_steps)) + \
                 list(np.linspace(two, three, second_segment_steps + 1))[1:] + \
                 list(np.linspace(three, four, third_segment_steps + 1))[1:]
        if noise:
            low = min(one, two, three, four)
            high = max(one, two, three, four)
            for ind in filter(lambda x: prices[x] not in [one, two, three, four], range(len(prices))):
                prices[ind] = min(max(prices[ind] + self.noise(), low), high)
        return prices

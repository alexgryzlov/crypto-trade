from logger.clock import Clock
from trading.timeframe import Timeframe


class ClockSimulator(Clock):
    def __init__(self, start, timeframe: Timeframe, candles_lifetime):
        self.start = start
        self.timeframe = timeframe
        self.seconds_per_candle = timeframe.to_seconds()
        self.candles_lifetime = candles_lifetime
        self.iteration = 0

    def get_timestamp(self):
        return self.start + self.iteration / self.candles_lifetime * self.seconds_per_candle

    def get_timeframe(self):
        return self.timeframe

    def get_seconds_per_candle(self):
        return self.seconds_per_candle

    def get_current_candle_lifetime(self):
        return self.iteration % self.candles_lifetime

    def next_iteration(self):
        self.iteration += 1

    def get_iterated_candles_count(self):
        return self.iteration // self.candles_lifetime

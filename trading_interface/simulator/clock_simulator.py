from logger.clock import Clock
from trading import Timeframe


class ClockSimulator(Clock):
    def __init__(self, start_ts: int, timeframe: Timeframe, candles_lifetime):
        self.start_ts = start_ts
        self.timeframe = timeframe
        self.seconds_per_candle = timeframe.to_seconds()
        self.candles_lifetime = candles_lifetime
        self.iteration = 0

    def get_timestamp(self):
        return int(self.start_ts + self.iteration / self.candles_lifetime * self.seconds_per_candle)

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

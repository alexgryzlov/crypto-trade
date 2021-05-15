from helpers.typing.common_types import Config

from logger.clock import Clock
from trading import Timeframe
from time import time


class WAVESExchangeClock(Clock):
    def __init__(self, config: Config):
        super().__init__()
        self._before_start_offset = config['before_start_offset']
        self._last_candle_fetch = self.get_timestamp() - self._before_start_offset

    def get_timestamp(self) -> int:
        return int(time())

    def get_waves_timestamp(self) -> int:
        return int(time() * 1000)

    def get_last_fetch(self) -> int:
        return self._last_candle_fetch

    def update_last_fetch(self, new_time: int) -> None:
        self._last_candle_fetch = new_time



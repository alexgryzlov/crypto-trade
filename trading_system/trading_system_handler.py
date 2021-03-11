from __future__ import annotations
import typing as tp

from trading_interface.trading_interface import TradingInterface


class TradingSystemHandler:
    def __init__(self, trading_interface: TradingInterface):
        self.ti = trading_interface
        self.last_candle_timestamp = -1

    def update(self) -> None:
        pass

    def get_required_handlers(self) -> tp.List[TradingSystemHandler]:
        """ For dependent handlers. """
        return []

    def link_required_handlers(self, handlers: tp.List[TradingSystemHandler]) \
            -> None:
        pass

    def get_name(self) -> str:
        """ Should be unique. """
        return type(self).__name__

    def received_new_candle(self) -> bool:
        last_candles = self.ti.get_last_n_candles(1)
        if last_candles:
            last_candle = last_candles[0]
            if last_candle.ts != self.last_candle_timestamp:
                self.last_candle_timestamp = last_candle.ts
                return True
        return False

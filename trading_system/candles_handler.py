from trading_system.trading_system_handler import TradingSystemHandler
from trading_interface.trading_interface import TradingInterface
from logger.log_events import NewCandleEvent
from logger.logger import Logger


class CandlesHandler(TradingSystemHandler):
    def __init__(self, trading_interface: TradingInterface):
        super().__init__(trading_interface)
        self.ti = trading_interface
        self.logger = Logger("CandlesHandler")

    def update(self) -> None:
        if super().received_new_candle():
            last_candle = self.ti.get_last_n_candles(1)[0]
            self.logger.trading(NewCandleEvent(last_candle))

    def get_last_candle_timestamp(self) -> int:
        return self.last_candle_timestamp

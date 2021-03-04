from trading_system.trading_system_handler import TradingSystemHandler
from trading_interface.trading_interface import TradingInterface
from logger import logger
from logger.log_events import MovingAverageEvent


class MovingAverageHandler(TradingSystemHandler):
    def __init__(self, trading_interface: TradingInterface, window_size):
        super().__init__(trading_interface)
        self.ti = trading_interface
        self.window_size = window_size
        self.average_values = []
        self.logger = logger.get_logger(f"MovingAverageHandler{self.window_size}")

    def update(self):
        if not super().received_new_candle():
            return
        candles = self.ti.get_last_n_candles(self.window_size)
        if len(candles) < self.window_size:
            return
        self.average_values.append(sum(c.get_mid_price() for c in candles) / self.window_size)
        self.logger.trading(MovingAverageEvent(self.average_values[-1], self.window_size))

    def get_n_average_values(self, n):
        return self.average_values[-n:]

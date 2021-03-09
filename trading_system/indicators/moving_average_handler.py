from trading_system.trading_system_handler import TradingSystemHandler
from trading_interface.trading_interface import TradingInterface
from logger.logger import Logger
from logger.log_events import MovingAverageEvent


class MovingAverageHandler(TradingSystemHandler):
    """ Simple Moving Average (SMA or MA) """
    def __init__(self, trading_interface: TradingInterface, window_size):
        super().__init__(trading_interface)
        self.ti = trading_interface

        self.window_size = window_size

        self.values = []
        self.logger = Logger(self.get_name())

    def get_name(self):
        return f'{type(self).__name__}{self.window_size}'

    def update(self):
        if not super().received_new_candle():
            return

        candles = self.ti.get_last_n_candles(self.window_size)
        if len(candles) < self.window_size:
            return

        candle_values = list(map(lambda c: c.get_mid_price(), candles))
        self.values.append(self.calculate_from(candle_values))
        self.logger.trading(MovingAverageEvent(self.get_last_n_values(1), self.window_size))

    def get_last_n_values(self, n):
        return self.values[-n:]

    @staticmethod
    def calculate_from(values):
        return sum(values) / len(values)

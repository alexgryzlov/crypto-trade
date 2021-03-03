from trading_system.indicators.exp_moving_average_handler import ExpMovingAverageHandler
from trading_system.trading_system_handler import TradingSystemHandler
from trading_interface.trading_interface import TradingInterface


class RelativeStrengthIndexHandler(TradingSystemHandler):
    """ Relative Strength Index (RSI) """
    def __init__(self, trading_interface: TradingInterface, window_size):
        super().__init__(trading_interface)
        self.ti = trading_interface

        self.window_size = window_size
        self.alpha = 1 / window_size

        self.relative_strength = []
        self.values = []

    def get_name(self):
        return f'{type(self).__name__}{self.window_size}'

    def update(self):
        if not super().received_new_candle():
            return

        candles = self.ti.get_last_n_candles(self.window_size)
        if len(candles) < self.window_size:
            return

        upwards = list(map(lambda c: max(c.get_delta(), 0), candles))
        downwards = list(map(lambda c: max(-c.get_delta(), 0), candles))
        self.relative_strength.append(ExpMovingAverageHandler.get_from(upwards, self.alpha) /
                                      ExpMovingAverageHandler.get_from(downwards, self.alpha))
        self.values.append(100 - 100 / (1 + self.relative_strength[-1]))

    def get_last_n_values(self, n):
        return self.values[-n:]

from math import isclose

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

        deltas = list(map(lambda c: c.get_delta(), candles))
        rs, rsi = self.calculate_from(deltas, self.alpha)
        self.relative_strength.append(rs)
        self.values.append(rsi)

    def get_last_n_values(self, n):
        return self.values[-n:]

    @staticmethod
    def calculate_from(deltas, alpha=None) -> [float, float]:
        """ Returns relative strength value and relative strength index. """
        if alpha is None:
            alpha = 1 / len(deltas)

        average_gain = ExpMovingAverageHandler.calculate_from(list(map(lambda x: max(x, 0), deltas)), alpha)
        average_loss = ExpMovingAverageHandler.calculate_from(list(map(lambda x: max(-x, 0), deltas)), alpha)

        if average_loss == 0:  # Avoid RuntimeWarning with zero division
            relative_strength = 1 if isclose(average_gain, 0, abs_tol=1e-7) else float('inf')
        else:
            relative_strength = average_gain / average_loss
        relative_strength_index = 100 - 100 / (1 + relative_strength)
        return relative_strength, relative_strength_index

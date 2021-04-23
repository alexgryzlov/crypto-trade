import typing as tp

import numpy as np

import trading_system.trading_system as ts
from trading import Signal, TrendType
from trading_signal_detectors.trading_signal_detector import \
    TradingSignalDetector
from trading_system.indicators.exp_moving_average_handler import \
    ExpMovingAverageHandler


class ExpMovingAverageSignalDetector(TradingSignalDetector):
    def __init__(
            self,
            trading_system: ts.TradingSystem,
            low: int = 8,
            mid: int = 14,
            high: int = 50,
            signal_length: int = 3,
            smooth: int = 2):
        self.ts = trading_system
        self.signal_length = signal_length
        self.low_handler: ExpMovingAverageHandler = \
            trading_system.handlers[f'ExpMovingAverageHandler{low}_{smooth}']
        self.mid_handler: ExpMovingAverageHandler = \
            trading_system.handlers[f'ExpMovingAverageHandler{mid}_{smooth}']
        self.high_handler: ExpMovingAverageHandler = \
            trading_system.handlers[f'ExpMovingAverageHandler{high}_{smooth}']

    def get_trading_signals(self) -> tp.List[Signal]:
        low_values = self.low_handler.get_last_n_values(self.signal_length)
        mid_values = self.mid_handler.get_last_n_values(self.signal_length)
        high_values = self.high_handler.get_last_n_values(self.signal_length)

        if len(low_values) < self.signal_length:
            return []

        mid_low_diff = np.array(mid_values) - np.array(low_values)
        high_mid_diff = np.array(high_values) - np.array(mid_values)

        if np.all(mid_low_diff > 0) and np.all(high_mid_diff > 0):
            return [Signal("exp_moving_average", TrendType.UPTREND)]

        if np.all(mid_low_diff < 0) and np.all(high_mid_diff < 0):
            return [Signal("exp_moving_average", TrendType.DOWNTREND)]

        return []

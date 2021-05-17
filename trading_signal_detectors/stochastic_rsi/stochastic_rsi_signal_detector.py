import typing as tp
import pandas as pd

import trading_system.trading_system as ts
from logger.logger import Logger
from trading import Signal, TrendType

from trading_signal_detectors.trading_signal_detector import TradingSignalDetector
from trading_system.indicators import RelativeStrengthIndexHandler


class StochasticRSISignalDetector(TradingSignalDetector):
    def __init__(self, trading_system: ts.TradingSystem,
                 rsi_len: int = 14, stoch_len: int = 14,
                 k: int = 3, d: int = 3):
        self.ts = trading_system
        self.logger = Logger('StochasticRSISignalDetector')
        self.rsi: RelativeStrengthIndexHandler = self.ts.add_handler(
            RelativeStrengthIndexHandler,
            params={"window_size": rsi_len})
        self.stoch_len = stoch_len
        self.k = k
        self.d = d
        self.prev_k_sma = 0.
        self.prev_d_sma = 0.

    def get_trading_signals(self) -> tp.List[Signal]:
        rsi_values = self.rsi.get_last_n_values(
            self.stoch_len + self.k + self.d - 1)

        if len(rsi_values) < self.stoch_len + self.k + self.d - 1:
            return []

        stoch_values = self.__calculate_stochastic(rsi_values)
        k_sma_values = self.__calculate_sma(stoch_values, self.k)
        d_sma_values = self.__calculate_sma(k_sma_values, self.d)
        k_sma = k_sma_values[-1]
        d_sma = d_sma_values[-1]
        trend: tp.Optional[TrendType] = None

        if (self.prev_k_sma < self.prev_d_sma) and (k_sma > d_sma):
            trend = TrendType.UPTREND

        if (self.prev_k_sma > self.prev_d_sma) and (k_sma < d_sma):
            trend = TrendType.DOWNTREND

        self.prev_k_sma = k_sma
        self.prev_d_sma = d_sma
        if trend is None:
            return []

        trend_type = 'uptrend' if trend == TrendType.UPTREND else 'downtrend'
        self.logger.info(f"SRSI {trend_type} detected")
        return [Signal("stochastic_rsi", trend)]

    def __calculate_stochastic(self, values: tp.List[float]) -> tp.List[float]:
        vals = pd.Series(values)
        low = vals.rolling(self.stoch_len).min()
        high = vals.rolling(self.stoch_len).max()
        return ((vals - low) / (high - low))[-(self.k + self.d - 1):].tolist()

    def __calculate_sma(self, values: tp.List[float],
                        window: int) -> tp.List[float]:
        rolling_mean = pd.Series(values).rolling(window).mean()
        return rolling_mean[-window:].tolist()

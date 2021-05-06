import numpy as np
import typing as tp

from helpers.updates_checker import UpdatesChecker, FromClass
from trading_signal_detectors.trading_signal_detector import TradingSignalDetector
from trading import Signal, TrendType
from trading_system.indicators import MovingAverageCDHandler
from trading_system.trading_system import TradingSystem

PRICE_EPS = 1e-5


class MACDSignalDetector(TradingSignalDetector):
    """
        Moving Average Convergence/Divergence(MACD)
        Uptrend signal when macd crosses signal line upwards
        Downtrend signal when macd crosses signal line downwards
    """
    def __init__(self, trading_system: TradingSystem):
        self.ts = trading_system
        self.handler: MovingAverageCDHandler = \
            trading_system.add_handler(MovingAverageCDHandler, params={})

    @UpdatesChecker.on_updates(FromClass(lambda detector: [detector.handler.get_name()]), [])
    def get_trading_signals(self) -> tp.List[Signal]:
        values = np.array(self.handler.get_last_n_values(2))

        if len(values) < 2:
            return []
        diff = values[:, 0] - values[:, 1]

        if diff[0] < -PRICE_EPS and diff[1] > PRICE_EPS:
            return [Signal("moving_average_cd", TrendType.UPTREND)]

        if diff[0] > PRICE_EPS and diff[1] < -PRICE_EPS:
            return [Signal("moving_average_cd", TrendType.DOWNTREND)]

        return []

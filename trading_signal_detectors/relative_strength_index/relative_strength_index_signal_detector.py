from helpers.updates_checker import UpdatesChecker, FromClass
from trading_signal_detectors.relative_strength_index.relative_strength_index_signal import RsiSignal, RsiSignalType
from trading_signal_detectors.trading_signal_detector import TradingSignalDetector
from trading import Signal
from trading_system.indicators import RelativeStrengthIndexHandler

from trading_system.trading_system import TradingSystem

PRICE_EPS = 0.05


class RelativeStrengthIndexSignalDetector(TradingSignalDetector):
    """
        Overbought signal when RSI > overbought_bound
        Oversold signal when RSI < oversold_bound
    """

    def __init__(self, trading_system: TradingSystem, window_size: int,
                 oversold_bound: float = 30, overbought_bound: float = 70):
        self.ts = trading_system
        self.oversold_bound = oversold_bound
        self.overbought_bound = overbought_bound
        self.handler: RelativeStrengthIndexHandler = \
            trading_system.handlers[f'RelativeStrengthIndexHandler{window_size}']

    @UpdatesChecker.on_updates(FromClass(lambda detector: [detector.handler.get_name()]), [])
    def get_trading_signals(self):
        values = self.handler.get_last_n_values(1)

        if len(values) < 1:
            return []

        if values[0] < self.oversold_bound:
            return [Signal("relative_strength_index",
                           RsiSignal(RsiSignalType.OVERSOLD,
                                     (self.oversold_bound - values[0]) / self.oversold_bound))]

        if values[0] > self.overbought_bound:
            return [Signal("relative_strength_index",
                           RsiSignal(RsiSignalType.OVERBOUGHT,
                                     (values[0] - self.overbought_bound) / (100 - self.overbought_bound)))]

        return []

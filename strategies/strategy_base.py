from trading import Trend, TrendType
import trading_system.trading_system as ts
from trading_signal_detectors.relative_strength_index.relative_strength_index_signal import RsiSignal


class StrategyBase:
    def __init__(self, **kwargs) -> None:
        pass

    def init_trading(self, trading_system: ts.TradingSystem) -> None:
        pass

    def update(self) -> None:
        pass

    def handle_new_trend_signal(self, trend: Trend) -> None:
        pass

    def handle_extremum_signal(self, trend: TrendType) -> None:
        pass

    def handle_moving_average_signal(self, trend: TrendType) -> None:
        pass

    def handle_moving_average_cd_signal(self, trend: TrendType) -> None:
        pass

    def handle_relative_strength_index_signal(self, signal: RsiSignal) -> None:
        pass

    def handle_filled_order_signal(self, order) -> None:
        pass

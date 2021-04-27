import typing as tp
from abc import ABC, abstractmethod

import trading_system.trading_system as ts
from trading_signal_detectors.trading_signal_detector import TradingSignalDetector
from trading import Trend, TrendType, Order, AssetPair


class StrategyBase(ABC):
    def __init__(self, **kwargs: tp.Any):
        pass

    @abstractmethod
    def init_trading(self, trading_system: ts.TradingSystem) -> None:
        pass

    @abstractmethod
    def update(self) -> None:
        pass

    def get_signal_generators(self) -> tp.List[TradingSignalDetector]:
        return []

    def handle_new_trend_signal(self, trend: Trend) -> None:
        pass

    def handle_extremum_signal(self, trend: TrendType) -> None:
        pass

    def handle_moving_average_signal(self, trend: TrendType) -> None:
        pass

    def handle_exp_moving_average_signal(self, trend: TrendType) -> None:
        pass

    def handle_stochastic_rsi_signal(self, trend: TrendType) -> None:
        pass

    def handle_filled_order_signal(self, order: Order) -> None:
        pass

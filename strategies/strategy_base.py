from trading import Trend, TrendType, Order, AssetPair
import trading_system.trading_system as ts
import typing as tp
from abc import ABC, abstractmethod


class StrategyBase(ABC):
    def __init__(self, **kwargs: tp.Any):
        pass

    @abstractmethod
    def init_trading(self, trading_system: ts.TradingSystem) -> None:
        pass

    @abstractmethod
    def update(self) -> None:
        pass

    def handle_new_trend_signal(self, trend: Trend) -> None:
        pass

    def handle_extremum_signal(self, trend: TrendType) -> None:
        pass

    def handle_moving_average_signal(self, trend: TrendType) -> None:
        pass

    def handle_filled_order_signal(self, order: Order) -> None:
        pass

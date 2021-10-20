from strategies.strategy_base import StrategyBase
import typing as tp
import trading_system.trading_system as ts


class StrategyMock(StrategyBase):
    def __init__(self, *args: tp.Any, **kwargs: tp.Any):
        pass

    def update(self) -> None:
        pass

    def init_trading(self, trading_system: ts.TradingSystem) -> None:
        pass

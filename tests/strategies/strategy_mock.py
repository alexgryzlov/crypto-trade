from strategies.strategy_base import StrategyBase
import typing as tp


class StrategyMock(StrategyBase):
    def __init__(self, *args: tp.Any, **kwargs: tp.Any):
        pass

    def update(self) -> None:
        pass

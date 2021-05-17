import trading_system.trading_system as ts
from strategies.strategy_base import StrategyBase

from logger.logger import Logger
from helpers.typing.common_types import Config

from trading import AssetPair, Order
from trading_system.trading_system import TradingSystem
import typing as tp
from trading import Direction


class GridStrategy(StrategyBase):
    def __init__(self, config: Config) -> None:
        self._asset_pair = AssetPair.from_string(*config['asset_pair'])
        self._total_levels: int = config['total_levels']
        self._base_level: int = config['base_level']
        self._base_price: float = config['base_price']
        self._interval: float = config['interval']
        self._tranche: float = config['tranche']
        self._window_size: int = config['window_size']
        self._grid: tp.Dict[str, int] = {}
        self._ts = None

    def get_level_price(self, level) -> float:
        return round(self._base_price * (1 + self._interval) ** (level - self._base_level), 4)

    def init_trading(self, trading_system: TradingSystem) -> None:
        self._ts = trading_system

        for level in range(0, self._base_level):
            order = self._ts.buy(self._asset_pair, self._tranche, self.get_level_price(level))
            if order is not None:
                self._grid[order.order_id] = level

        for level in range(self._base_level + 1, self._total_levels):
            order = self._ts.sell(self._asset_pair, self._tranche, self.get_level_price(level))
            if order is not None:
                self._grid[order.order_id] = level

    def update(self) -> None:
        pass

    def handle_filled_order_signal(self, order: Order) -> None:
        if order.direction.value == Direction.SELL.value:
            level = self._grid[order.order_id]
            self._grid.pop(order.order_id)
            order = self._ts.buy(self._asset_pair, self._tranche, self.get_level_price(level - 1))
            if order is not None:
                self._grid[order.order_id] = level - 1
        elif order.direction.value == Direction.BUY.value:
            level = self._grid[order.order_id]
            self._grid.pop(order.order_id)
            order = self._ts.sell(self._asset_pair, self._tranche, self.get_level_price(level + 1))
            if order is not None:
                self._grid[order.order_id] = level + 1

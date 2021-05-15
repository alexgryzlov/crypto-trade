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
        self.logger = Logger('GridStrategy')
        self.asset_pair = AssetPair.from_string(*config['asset_pair'])
        self.total_levels: int = config['total_levels']
        self.base_level: int = config['base_level']
        self.base_price: float = config['base_price']
        self.interval: float = config['interval']
        self.tranche: float = config['tranche']
        self.window_size: int = config['window_size']
        self.grid: tp.Dict[str, int] = {}
        self.ts = None

    def get_level_price(self, level) -> float:
        return round(self.base_price * (1 + self.interval) ** (level - self.base_level), 4)

    def init_trading(self, trading_system: TradingSystem) -> None:
        self.ts = trading_system

        for level in range(0, self.base_level):
            order = self.ts.buy(self.asset_pair, self.tranche, self.get_level_price(level))
            self.grid[order.order_id] = level

        for level in range(self.base_level + 1, self.total_levels):
            order = self.ts.sell(self.asset_pair, self.tranche, self.get_level_price(level))
            self.grid[order.order_id] = level

    def update(self) -> None:
        pass

    def handle_filled_order_signal(self, order: Order) -> None:
        if order.direction.value == Direction.SELL.value:
            level = self.grid[order.order_id]
            self.grid.pop(order.order_id)
            order = self.ts.buy(self.tranche, self.get_level_price(level - 1))
            self.grid[order.order_id] = level
        elif order.direction.value == Direction.BUY.value:
            level = self.grid[order.order_id]
            self.grid.pop(order.order_id)
            order = self.ts.sell(self.tranche, self.get_level_price(level + 1))
            self.grid[order.order_id] = level

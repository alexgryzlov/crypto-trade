import trading_system.trading_system as ts
from strategies.strategy_base import StrategyBase

from logger.logger import Logger

from trading import Trend, TrendType, Asset, AssetPair, Order
import trading_system.trading_system as ts
import typing as tp
from trading import Direction


class GridStrategy(StrategyBase):
    def __init__(self, **kwargs: tp.Any) -> None:
        self.asset_pair = AssetPair(Asset('USDT'), Asset('USDN'))
        self.logger = Logger('GridStrategy')
        self.ts = None
        self.total_levels = 13
        self.base_level = 6
        self.base_price = 1.001
        self.interval = 0.002
        self.tranche = 100
        self.window_size = 20
        self.grid = {}

    def get_level_price(self, level):
        return round(self.base_price * (1 + self.interval) ** (level - self.base_level), 4)

    def init_trading(self, trading_system: ts.TradingSystem) -> None:
        self.ts = trading_system

        for level in range(0, self.base_level):
            order = self.ts.buy(self.asset_pair, self.tranche, self.get_level_price(level))
            self.grid[order.order_id] = level

        for level in range(self.base_level + 1, self.total_levels):
            order = self.ts.sell(self.asset_pair, self.tranche, self.get_level_price(level))
            self.grid[order.order_id] = level

    def update(self) -> None:
        pass

    def handle_filled_order_signal(self, order: Order):
        if order.direction.value == Direction.SELL.value:
            level = self.grid[order.order_id]
            self.grid.pop(order.order_id)
            order = self.ts.buy(self.asset_pair, self.tranche, self.get_level_price(level - 1))
            self.grid[order.order_id] = level
        elif order.direction.value == Direction.BUY.value:
            level = self.grid[order.order_id]
            self.grid.pop(order.order_id)
            order = self.ts.sell(self.asset_pair, self.tranche, self.get_level_price(level + 1))
            self.grid[order.order_id] = level

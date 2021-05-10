import typing as tp

import trading_system.trading_system as ts
from strategies.strategy_base import StrategyBase

from helpers.typing.common_types import Config
from logger.logger import Logger

from trading import Asset, AssetPair, Order, Direction
from helpers.ceil import ceil


class GridStrategy(StrategyBase):
    def __init__(self, config: Config) -> None:
        self.asset_pair = AssetPair(*[Asset(x) for x in config['asset_pair']])
        self.logger = Logger('GridStrategy')
        self.ts = None
        self.total_levels = config['total_levels']
        self.base_level = self.total_levels // 2
        self.base_price = 1.001
        self.interval = 0.002
        self.min_amount = 10
        self.grid = {}

    def get_level_price(self, level):
        return round(self.base_price * (1 + self.interval) ** (level - self.base_level), 4)

    def init_trading(self, trading_system: ts.TradingSystem) -> None:
        self.ts = trading_system
        self.place_orders()

    def update(self) -> None:
        pass

    def place_orders(self) -> None:
        price_asset = self.ts.wallet[self.asset_pair.price_asset]
        amount_asset = self.ts.wallet[self.asset_pair.amount_asset]

        if price_asset > self.min_amount:
            buy_amount = ceil(price_asset / self.base_level, 4)
            for level in range(0, self.base_level):
                order = self.ts.buy(self.asset_pair, buy_amount, self.get_level_price(level))
                if order is not None:
                    self.grid[order.order_id] = level

        if amount_asset > self.min_amount:
            sell_amount = ceil(amount_asset / self.base_level, 4)
            for level in range(self.base_level + 1, self.total_levels):
                order = self.ts.sell(self.asset_pair, sell_amount, self.get_level_price(level))
                if order is not None:
                    self.grid[order.order_id] = level

    def handle_filled_order_signal(self, order: Order):
        if order.direction.value == Direction.SELL.value:
            level = self.grid[order.order_id]
            self.grid.pop(order.order_id)
            order = self.ts.buy(self.asset_pair, order.amount, self.get_level_price(level - 1))
            if order is not None:
                self.grid[order.order_id] = level
        elif order.direction.value == Direction.BUY.value:
            level = self.grid[order.order_id]
            self.grid.pop(order.order_id)
            order = self.ts.sell(self.asset_pair, order.amount, self.get_level_price(level + 1))
            if order is not None:
                self.grid[order.order_id] = level

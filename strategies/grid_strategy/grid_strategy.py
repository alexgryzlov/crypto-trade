import typing as tp

import trading_system.trading_system as ts
from strategies.strategy_base import StrategyBase

from logger.logger import Logger
from helpers.typing.common_types import Config
from helpers.floor import floor

from trading import Asset, AssetPair, Order, Direction
from trading_system.trading_system import TradingSystem
from trading import Direction


class GridStrategy(StrategyBase):
    def __init__(self, config: Config) -> None:
        self.logger = Logger('GridStrategy')
        self._asset_pair = AssetPair(*config['asset_pair'])
        self._total_levels: int = config['total_levels']
        self._base_level: int = self._total_levels // 2
        self._base_price: float = config['base_price']
        self._interval: float = config['interval']
        self._window_size: int = config['window_size']
        self._grid: tp.Dict[str, int] = {}
        self._min_amount = config['min_amount']
        self._ts = None

    def get_level_price(self, level) -> float:
        return round(self._base_price * (1 + self._interval) ** (level - self._base_level), 4)

    def init_trading(self, trading_system: ts.TradingSystem) -> None:
        self._ts = trading_system
        self.place_orders()

    def place_orders(self) -> None:
        price_asset = self._ts.wallet[self._asset_pair.price_asset]
        amount_asset = self._ts.wallet[self._asset_pair.amount_asset]

        if price_asset > self._min_amount:
            buy_amount = floor(price_asset / self._base_level, 4)
            for level in range(0, self._base_level):
                order = self._ts.buy(self._asset_pair, buy_amount, self.get_level_price(level))
                if order is not None:
                    self._grid[order.order_id] = level

        if amount_asset > self._min_amount:
            sell_amount = floor(amount_asset / self._base_level, 4)
            for level in range(self._base_level + 1, self._total_levels):
                order = self._ts.sell(self._asset_pair, sell_amount, self.get_level_price(level))
                if order is not None:
                    self._grid[order.order_id] = level

    def update(self) -> None:
        pass

    def handle_filled_order_signal(self, order: Order):
        if order.direction.value == Direction.SELL.value:
            level = self._grid[order.order_id]
            self._grid.pop(order.order_id)
            order = self._ts.buy(self._asset_pair, order.amount, self.get_level_price(level - 1))
            if order is not None:
                self._grid[order.order_id] = level
        elif order.direction.value == Direction.BUY.value:
            level = self._grid[order.order_id]
            self._grid.pop(order.order_id)
            order = self._ts.sell(self._asset_pair, order.amount, self.get_level_price(level + 1))
            if order is not None:
                self._grid[order.order_id] = level

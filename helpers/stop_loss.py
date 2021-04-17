import typing as tp
from copy import copy

from logger.logger import Logger
from trading import Order
from trading_system.trading_system import TradingSystem


class StopLoss():
    def __init__(self, ts: TradingSystem):
        self.orders: tp.List[tp.Tuple[Order, float]] = []
        self.ts = ts
        self.logger = Logger('StopLoss')

    def set_stop_loss(self, order: Order, price: float) -> None:
        self.orders.append((order, price))

    def update(self) -> None:
        for order, price in copy(self.orders):
            sgn = -int(order.direction)
            curr_price = self.ts.get_price_by_direction(sgn)
            if sgn * curr_price <= sgn * price:
                self.ts.create_order(order.asset_pair, -sgn * order.amount)
                self.orders.remove((order, price))
                self.logger.info(f'Stop-loss trigger at price {curr_price}')

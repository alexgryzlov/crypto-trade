import typing as tp
from copy import copy

from logger.logger import Logger
from trading import Direction, Order
from trading_system.trading_system import TradingSystem


class LimitOrder():
    def __init__(self, ts: TradingSystem):
        self.orders: tp.List[tp.Tuple[Order,
                             tp.Optional[float], tp.Optional[float]]] = []
        self.ts = ts
        self.logger = Logger('LimitOrder')

    def set_limit(
            self,
            order: Order,
            take_profit: tp.Optional[float],
            stop_loss: tp.Optional[float]) -> None:
        self.orders.append((order, take_profit, stop_loss))

    def update(self) -> None:
        for order, take_profit, stop_loss in copy(self.orders):
            if not self.ts.order_is_filled(order):
                continue
            direction = Direction(-order.direction)
            sgn = int(direction)
            cur_price = self.ts.get_price_by_direction(order.direction)
            if take_profit is not None and sgn * cur_price > sgn * take_profit:
                self.ts.create_order(order.asset_pair, -sgn * order.amount)
                self.orders.remove((order, take_profit, stop_loss))
                self.logger.info(f'Take-profit trigger at price {cur_price}')
            if stop_loss is not None and sgn * cur_price < sgn * stop_loss:
                self.ts.create_order(order.asset_pair, -sgn * order.amount)
                self.orders.remove((order, take_profit, stop_loss))
                self.logger.info(f'Stop-loss trigger at price {cur_price}')

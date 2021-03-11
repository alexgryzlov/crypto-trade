from trading_system.trading_system_handler import TradingSystemHandler
from trading_interface.trading_interface import TradingInterface

from trading import Order

from logger.log_events import FilledOrderEvent
from logger.logger import Logger

import typing as tp


class OrdersHandler(TradingSystemHandler):
    def __init__(self, trading_interface: TradingInterface):
        super().__init__(trading_interface)
        self.ti = trading_interface
        self.logger = Logger("OrdersHandler")
        self.active_orders: tp.List[Order] = []
        self.new_filled_orders: tp.List[Order] = []

    def update(self) -> None:
        filled_orders = [order for order in self.active_orders if
                         self.ti.order_is_filled(order)]
        for order in filled_orders:
            self.logger.trading(FilledOrderEvent(order.order_id))
        self.new_filled_orders += filled_orders
        self.active_orders = [order for order in self.active_orders if
                              not self.ti.order_is_filled(order)]

    def get_active_orders(self) -> tp.List[Order]:
        return self.active_orders

    def get_new_filled_orders(self) -> tp.List[Order]:
        orders = self.new_filled_orders
        self.new_filled_orders = []
        return orders

    def add_new_order(self, order: Order) -> None:
        self.active_orders.append(order)

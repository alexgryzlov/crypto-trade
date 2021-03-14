import typing as tp

from trading import Order


class TradingStatistics:
    def __init__(self) -> None:
        self.filled_orders: tp.List[Order] = []

    def set_initial_balance(self, balance: int) -> None:
        pass

    def add_filled_order(self, order: Order):
        self.filled_orders.append(order)

    def get_stats(self) -> str:
        pass

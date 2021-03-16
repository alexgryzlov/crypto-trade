import math
import typing as tp

from trading import Order


class TradingStatistics:
    def __init__(self, initial_balance: tp.Optional[float] = None) -> None:
        self.initial_balance = initial_balance
        self.final_balance = None
        self.filled_orders: tp.List[Order] = []

    def set_initial_balance(self, balance: float) -> None:
        self.initial_balance = balance

    def set_final_balance(self, balance: float) -> None:
        self.final_balance = balance

    def add_filled_order(self, order: Order) -> None:
        self.filled_orders.append(order)

    def __str__(self) -> str:
        return f'initial balance: {self.initial_balance:.2f}\n' \
               f'final balance:   {self.final_balance:.2f}\n' \
               f'delta:           {self._calc_absolute_delta():.2f}\n' \
               f'delta(%):        {self._calc_relative_delta():.1f}%\n' \
               f'filled orders:   {len(self.filled_orders)}'

    def _calc_absolute_delta(self) -> float:
        return self.final_balance - self.initial_balance

    def _calc_relative_delta(self) -> float:
        if math.isclose(self.initial_balance, 0):
            return 0
        return self._calc_absolute_delta() / self.initial_balance * 100

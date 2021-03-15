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
        return f'initial balance: {round(self.initial_balance, 2)}\n' \
               f'final balance:   {round(self.final_balance, 2)}\n' \
               f'delta:           {round(self._calc_absolute_delta(), 2)}\n' \
               f'delta(%):        {round(self._calc_relative_delta(), 2)}%\n' \
               f'filled orders:   {len(self.filled_orders)}'

        # return 'initial balance: {:.2f}'.format(self.initial_balance) + \
        #        'final balance:   {:.2f}'.format()

    def _calc_absolute_delta(self) -> float:
        return self.final_balance - self.initial_balance

    def _calc_relative_delta(self) -> float:
        if math.isclose(self.initial_balance, 0):
            return 0
        return self._calc_absolute_delta() / self.initial_balance * 100

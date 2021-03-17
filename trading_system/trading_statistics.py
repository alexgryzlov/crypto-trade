import math
import typing as tp

from trading import Order, Timestamp


class TradingStatistics:
    def __init__(self,
                 initial_balance: tp.Optional[float] = None,
                 start_timestamp: tp.Optional[int] = None) -> None:
        self.initial_balance = initial_balance
        self.final_balance = None
        self.start_timestamp = start_timestamp
        self.finish_timestamp = None
        self.filled_orders: tp.List[Order] = []

    def set_initial_balance(self, balance: float) -> None:
        self.initial_balance = balance

    def set_final_balance(self, balance: float) -> None:
        self.final_balance = balance

    def set_start_timestamp(self, timestamp: int) -> None:
        self.start_timestamp = timestamp

    def set_finish_timestamp(self, timestamp: int) -> None:
        self.finish_timestamp = timestamp

    def add_filled_order(self, order: Order) -> None:
        self.filled_orders.append(order)

    def add_filled_orders(self, orders: tp.List[Order]) -> None:
        for order in orders:
            self.filled_orders.append(order)

    def __str__(self) -> str:
        return f'{Timestamp.to_iso_format(self.start_timestamp)} - {Timestamp.to_iso_format(self.finish_timestamp)}\n' \
               f'initial balance: {self.initial_balance:.2f}\n' \
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

    @staticmethod
    def merge(stats_array: tp.List['TradingStatistics']) -> 'TradingStatistics':
        stats = TradingStatistics()
        stats.set_initial_balance(sum([s.initial_balance for s in stats_array]))
        stats.set_final_balance(sum([s.final_balance for s in stats_array]))
        stats.set_start_timestamp(min([s.start_timestamp for s in stats_array]))
        stats.set_finish_timestamp(max([s.finish_timestamp for s in stats_array]))
        for s in stats_array:
            stats.add_filled_orders(s.filled_orders)
        return stats

    @staticmethod
    def get_final_balance(stats_array: tp.List['TradingStatistics']) -> tp.List[float]:
        return [s.final_balance for s in stats_array]

    @staticmethod
    def get_start_timestamp(stats_array: tp.List['TradingStatistics']) -> tp.List[int]:
        return [s.start_timestamp for s in stats_array]

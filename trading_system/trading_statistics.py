import math
import typing as tp
import plotly.graph_objects as go

from trading import Order, Timestamp


class TradingStatistics:
    def __init__(self,
                 initial_balance: tp.Optional[float] = None,
                 start_timestamp: tp.Optional[int] = None) -> None:
        self.initial_balance = initial_balance
        self.final_balance: tp.Optional[float] = None
        self.start_timestamp = start_timestamp
        self.finish_timestamp: tp.Optional[int] = None
        self.filled_order_count = 0

    def set_initial_balance(self, balance: float) -> None:
        self.initial_balance = balance

    def set_final_balance(self, balance: float) -> None:
        self.final_balance = balance

    def set_start_timestamp(self, timestamp: int) -> None:
        self.start_timestamp = timestamp

    def set_finish_timestamp(self, timestamp: int) -> None:
        self.finish_timestamp = timestamp

    def add_filled_order(self, _order: Order) -> None:
        self.filled_order_count += 1

    def __str__(self) -> str:
        if self.start_timestamp is None or self.finish_timestamp is None:
            raise ValueError('finish_timestamp hasn\'t been set')
        return f'{Timestamp.to_iso_format(self.start_timestamp)} - {Timestamp.to_iso_format(self.finish_timestamp)}\n' \
               f'initial balance: {self.initial_balance:.2f}\n' \
               f'final balance:   {self.final_balance:.2f}\n' \
               f'delta:           {self._calc_absolute_delta():.2f}\n' \
               f'delta(%):        {self._calc_relative_delta():.1f}%\n' \
               f'filled orders:   {self.filled_order_count}'

    def _calc_absolute_delta(self) -> float:
        return self.final_balance - self.initial_balance

    def _calc_relative_delta(self) -> float:
        if math.isclose(self.initial_balance, 0):
            return 0
        return self._calc_absolute_delta() / self.initial_balance * 100

    @classmethod
    def merge(cls, stats_array: tp.List['TradingStatistics']) -> 'TradingStatistics':
        stats = cls()
        stats.set_initial_balance(sum([s.initial_balance for s in stats_array]))
        stats.set_final_balance(sum([s.final_balance for s in stats_array]))
        stats.set_start_timestamp(min([s.start_timestamp for s in stats_array]))
        stats.set_finish_timestamp(max([s.finish_timestamp for s in stats_array]))
        stats.filled_order_count = sum([s.filled_order_count for s in stats_array])
        return stats

    @staticmethod
    def get_absolute_delta(stats_array: tp.List['TradingStatistics']) -> tp.List[float]:
        return [s._calc_absolute_delta() for s in stats_array]

    @staticmethod
    def get_start_time(stats_array: tp.List['TradingStatistics']) -> tp.List[str]:
        return [Timestamp.to_iso_format(s.start_timestamp) for s in stats_array]

    @staticmethod
    def visualize(stats_array: tp.List['TradingStatistics']):
        stats_array.sort(key=lambda r: r.start_timestamp)
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=TradingStatistics.get_start_time(stats_array),
            y=TradingStatistics.get_absolute_delta(stats_array),
            marker_color=['green' if balance > 0 else 'red'
                          for balance in TradingStatistics.get_absolute_delta(stats_array)]))
        fig.show()

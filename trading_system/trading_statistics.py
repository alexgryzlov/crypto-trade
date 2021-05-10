import math
import typing as tp
from copy import copy
from collections import Counter

import plotly.graph_objects as go
from rich.box import Box
from rich.console import Console
from rich.table import Table

from helpers.typing.utils import require
from trading import Asset, Order, Timestamp

TABLE_STYLE: Box = Box(
    """\
┏━┳┓
┃ ┃┃
┡━╇┩
│ ││
├─┼┤
╞═╪╡
│ ││
╰─┴╯
"""
)


class TradingStatistics:
    def __init__(self,
                 price_asset: tp.Optional[Asset] = None,
                 initial_wallet: tp.Optional[tp.Dict[Asset, float]] = None,
                 initial_balance: tp.Optional[float] = None,
                 start_timestamp: tp.Optional[int] = None,
                 initial_coin_balance: tp.Optional[float] = None) -> None:
        self.initial_balance = initial_balance
        self.initial_coin_balance = initial_coin_balance
        self.price_asset = price_asset
        self.initial_wallet = copy(initial_wallet)
        self.final_wallet: tp.Optional[tp.Dict[Asset, float]] = None
        self.final_balance: tp.Optional[float] = None
        self.hodl_result: tp.Optional[float] = None
        self.start_timestamp = start_timestamp
        self.finish_timestamp: tp.Optional[int] = None
        self.filled_order_count = 0

    def set_hodl_result(self, balance: float) -> None:
        self.hodl_result = balance

    def set_price_asset(self, asset: Asset) -> None:
        self.price_asset = asset

    def set_initial_wallet(self, wallet: tp.Dict[Asset, float]) -> None:
        self.initial_wallet = copy(wallet)

    def set_initial_balance(self, balance: float) -> None:
        self.initial_balance = balance

    def set_final_wallet(self, wallet: tp.Dict[Asset, float]) -> None:
        self.final_wallet = copy(wallet)

    def set_final_balance(self, balance: float) -> None:
        self.final_balance = balance

    def set_start_timestamp(self, timestamp: int) -> None:
        self.start_timestamp = timestamp

    def set_finish_timestamp(self, timestamp: int) -> None:
        self.finish_timestamp = timestamp

    def add_filled_order(self, _order: Order) -> None:
        self.filled_order_count += 1

    def pretty_print(self) -> None:
        color = 'green' if self.calc_relative_delta() > 0 else 'red'
        console = Console()
        table = Table(show_footer=True, box=TABLE_STYLE, show_lines=True,
            title=f'{Timestamp.to_iso_format(require(self.start_timestamp))} - '
                  f'{Timestamp.to_iso_format(require(self.finish_timestamp))}')
        table.add_column('')
        table.add_column('Initial', f'Filled orders: {self.filled_order_count}')
        table.add_column('Final', f'Profit: [{color}]{self.calc_relative_delta():.1f}%[/{color}]\nHODL:   [{color}]{self._calc_absolute_hodl_delta():.1f}%[/{color}]')
        table.add_row('Balance', f'{require(self.initial_balance):.2f} {require(self.price_asset)}',
                      f'{require(self.final_balance):.2f} {require(self.price_asset)}')
        table.add_row('Wallet',
            self._wallet_pretty_format(require(self.initial_wallet)),
            self._wallet_pretty_format(require(self.final_wallet)))
        console.print(table)

    def __str__(self) -> str:
        return f"""\
{Timestamp.to_iso_format(require(self.start_timestamp))} - {Timestamp.to_iso_format(require(self.finish_timestamp))}
initial wallet ({require(self.initial_balance):.2f} {require(self.price_asset)}):
{self._wallet_pretty_format(require(self.initial_wallet))}
final wallet ({require(self.final_balance):.2f} {require(self.price_asset)}):
{self._wallet_pretty_format(require(self.final_wallet))}
delta:                  {self.calc_absolute_delta():.2f}
delta(%):               {self.calc_relative_delta():.1f}%
filled orders:          {self.filled_order_count}
--------------------------------------------------------
hodl_result:            {require(self.hodl_result):.2f}
delta hodl_result:      {require(self.hodl_result) - require(self.initial_balance):.2f}
delta hodl_result(%):   {self._calc_absolute_hodl_delta():.1f}%
"""

    def calc_absolute_delta(self) -> float:
        return require(self.final_balance) - require(self.initial_balance)

    def calc_relative_delta(self) -> float:
        if math.isclose(require(self.initial_balance), 0):
            return 0
        return self.calc_absolute_delta() / require(self.initial_balance) * 100

    def _calc_absolute_hodl_delta(self) -> float:
        if math.isclose(require(self.initial_balance), 0):
            return 0
        return (require(self.hodl_result) - require(self.initial_balance)) / require(self.initial_balance) * 100

    def _wallet_pretty_format(self, wallet: tp.Dict[Asset, float]) -> str:
        return '\n'.join([f'{asset}: {amount}' for asset, amount in wallet.items()])

    @classmethod
    def merge(cls, stats_array: tp.List['TradingStatistics']) -> 'TradingStatistics':
        if not stats_array:
            raise ValueError("empty stats array")

        stats = cls()
        stats.set_price_asset(require(stats_array[0].price_asset))
        stats.set_initial_wallet(dict(sum([Counter(require(x.initial_wallet)) for x in stats_array], Counter())))
        stats.set_initial_balance(sum([require(s.initial_balance) for s in stats_array]))
        stats.set_hodl_result(sum([require(s.hodl_result) for s in stats_array]))
        stats.set_final_wallet(dict(sum([Counter(require(x.final_wallet)) for x in stats_array], Counter())))
        stats.set_final_balance(sum([require(s.final_balance) for s in stats_array]))
        stats.set_start_timestamp(min([require(s.start_timestamp) for s in stats_array]))
        stats.set_finish_timestamp(max([require(s.finish_timestamp) for s in stats_array]))
        stats.filled_order_count = sum([s.filled_order_count for s in stats_array])
        return stats

    @staticmethod
    def get_absolute_delta(stats_array: tp.List['TradingStatistics']) -> tp.List[float]:
        return [s.calc_absolute_delta() for s in stats_array]

    @staticmethod
    def get_start_time(stats_array: tp.List['TradingStatistics']) -> tp.List[str]:
        return [Timestamp.to_iso_format(require(s.start_timestamp)) for s in stats_array]

    @staticmethod
    def visualize(stats_array: tp.List['TradingStatistics']) -> None:
        stats_array.sort(key=lambda r: r.start_timestamp)
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=TradingStatistics.get_start_time(stats_array),
            y=TradingStatistics.get_absolute_delta(stats_array),
            marker_color=['green' if balance > 0 else 'red'
                          for balance in TradingStatistics.get_absolute_delta(stats_array)]))
        fig.show()

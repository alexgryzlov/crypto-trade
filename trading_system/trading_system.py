from __future__ import annotations
import typing as tp

from collections import defaultdict, OrderedDict
from copy import copy

from helpers.typing.common_types import Config

from trading_interface.trading_interface import TradingInterface
from trading_system.candles_handler import CandlesHandler
from trading_system.trading_system_handler import TradingSystemHandler
from trading_system.trend_handler import TrendHandler
from trading_system.indicators import *
from trading_system.orders_handler import OrdersHandler

from trading_system.trading_statistics import TradingStatistics

from logger.log_events import BuyEvent, SellEvent, CancelEvent
from logger.logger import Logger

from trading import Asset, AssetPair, Signal, Order, Direction, Candle

from helpers.typing import TradingSystemHandlerT

PRICE_EPS = 0.005


class Handlers(OrderedDict):  # type: ignore
    def add(self, handler: TradingSystemHandler) -> Handlers:
        if handler.get_name() in self.keys():
            return self

        handlers = handler.get_required_handlers()
        for i, dependent_handler in enumerate(handlers):
            if dependent_handler.get_name() in self.keys():
                handlers[i] = self[dependent_handler.get_name()]
            else:
                self.add(dependent_handler)

        handler.link_required_handlers(handlers)
        self[handler.get_name()] = handler
        return self


class TradingSystem:
    def __init__(self, trading_interface: TradingInterface, config: Config):
        self.logger = Logger('TradingSystem')
        self.ti = trading_interface
        self.currency_asset = Asset(config['currency_asset'])
        self.wallet: tp.Dict[Asset, float] = {}
        for asset_name, amount in config['wallet'].items():
            self.wallet[Asset(asset_name)] = amount
        self.stats = TradingStatistics(
            initial_balance=self.get_total_balance(),
            start_timestamp=self.ti.get_timestamp())
        self.trading_signals: tp.List[Signal] = []
        self.handlers = Handlers() \
            .add(CandlesHandler(trading_interface)) \
            .add(OrdersHandler(trading_interface)) \
            .add(TrendHandler(trading_interface)) \
            .add(MovingAverageHandler(trading_interface, 25)) \
            .add(MovingAverageHandler(trading_interface, 50))
        self.logger.info('Trading system initialized')

    def stop_trading(self) -> None:
        self.cancel_all()
        for asset, amount in self.wallet.items():
            if asset != self.currency_asset:
                self.create_order(asset_pair=AssetPair(asset, self.currency_asset),
                                  amount=-amount)

    def get_trading_statistics(self) -> TradingStatistics:
        stats = copy(self.stats)
        stats.set_final_balance(self.get_total_balance())
        stats.set_finish_timestamp(self.get_timestamp())
        return stats

    def update(self) -> None:
        for handler in self.handlers.values():
            handler.update()

        for order in self.get_handler(OrdersHandler).get_new_filled_orders():
            self.stats.add_filled_order(copy(order))
            self.wallet[order.asset_pair.main_asset] -= \
                int(order.direction) * order.amount
            self.trading_signals.append(Signal('filled_order', copy(order)))

    def get_trading_signals(self) -> tp.List[Signal]:
        signals = self.trading_signals
        self.trading_signals = []
        return signals

    def exchange_is_alive(self) -> bool:
        return self.ti.is_alive()

    def get_timestamp(self) -> int:
        return self.ti.get_timestamp()

    def create_order(self, asset_pair: AssetPair, amount: float) -> tp.Optional[Order]:
        if amount > 0:
            return self.buy(asset_pair, amount, self.get_sell_price())
        elif amount < 0:
            return self.sell(asset_pair, -amount, self.get_buy_price())
        return None

    def buy(self, asset_pair: AssetPair, amount: float, price: float) -> tp.Optional[Order]:
        if self.wallet[asset_pair.secondary_asset] < price * amount:
            self.logger.warning(
                f"Not enough {asset_pair.secondary_asset}. "
                f"Order is not placed.")
            return None

        order = self.ti.buy(asset_pair, amount, price)
        self.logger.trading(BuyEvent(asset_pair.main_asset,
                                     asset_pair.secondary_asset,
                                     amount,
                                     price,
                                     order.order_id))
        self.get_handler(OrdersHandler).add_new_order(copy(order))
        return order

    def sell(self, asset_pair: AssetPair, amount: float, price: float) -> tp.Optional[Order]:
        if self.wallet[asset_pair.main_asset] < amount:
            self.logger.warning(
                f"Not enough {asset_pair.main_asset}. "
                f"Order is not placed.")
            return None

        order = self.ti.sell(asset_pair, amount, price)
        self.logger.trading(SellEvent(asset_pair.main_asset,
                                      asset_pair.secondary_asset,
                                      amount,
                                      price,
                                      order.order_id))
        self.get_handler(OrdersHandler).add_new_order(copy(order))
        return order

    def cancel_order(self, order: Order) -> None:
        self.ti.cancel_order(order)
        self.logger.trading(CancelEvent(order))
        self.get_handler(OrdersHandler).cancel_order(order)

    def cancel_all(self) -> None:
        self.ti.cancel_all()
        for order in self.get_handler(OrdersHandler).get_active_orders():
            self.logger.trading(CancelEvent(order))
        self.get_handler(OrdersHandler).cancel_all()

    def order_is_filled(self, order: Order) -> bool:
        return self.ti.order_is_filled(order)

    def get_price_by_direction(self, direction: Direction) -> float:
        return self.get_buy_price() if direction == Direction.BUY else self.get_sell_price()

    def get_buy_price(self) -> float:
        return self.ti.get_buy_price() - PRICE_EPS

    def get_sell_price(self) -> float:
        return self.ti.get_sell_price() + PRICE_EPS

    def get_active_orders(self) -> tp.Set[Order]:
        return self.get_handler(OrdersHandler).get_active_orders()

    def get_balance(self) -> float:
        balance = self.wallet[self.currency_asset]
        self.logger.info(f'Checking balance: {balance}')
        return balance

    def get_total_balance(self) -> float:
        total_balance = 0.0
        for asset, amount in self.wallet.items():
            if asset == self.currency_asset:
                total_balance += amount
            else:
                direction = Direction.from_value(-amount)
                total_balance += amount * int(direction) * self.get_price_by_direction(direction)
        return total_balance

    def get_wallet(self) -> tp.Dict[Asset, float]:
        self.logger.info(f'Checking wallet: {self.wallet.items()}')
        return copy(self.wallet)

    def get_last_n_candles(self, n: int) -> tp.List[Candle]:
        return self.ti.get_last_n_candles(n)

    def get_handler(self, cls: tp.Type[TradingSystemHandlerT]) \
            -> TradingSystemHandlerT:
        return self.handlers[cls.__name__]

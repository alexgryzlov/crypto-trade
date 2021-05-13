from __future__ import annotations

from collections import OrderedDict
from copy import copy
import math
import typing as tp

from helpers.typing.common_types import Config

from trading_interface.trading_interface import TradingInterface

from trading_system.candles_handler import CandlesHandler
from trading_system.orders_handler import OrdersHandler
from trading_system.trading_statistics import TradingStatistics
from trading_system.risk_checker import RiskChecker
from trading_system.indicators import *

from logger.log_events import BuyEvent, SellEvent, CancelEvent
from logger.logger import Logger

from trading import Asset, AssetPair, Signal, Order, Direction, Candle

from helpers.typing import TradingSystemHandlerT
from helpers.typing.utils import require


class Handlers(OrderedDict):  # type: ignore
    def add(self, handler: TradingSystemHandlerT) -> Handlers:
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
        self._logger = Logger('TradingSystem')
        self._ti = trading_interface
        self._risk_checker = RiskChecker(
            trading_interface=trading_interface,
            config=config["risk_checker"])

        self._currency_asset = Asset(config['currency_asset'])
        self._wallet: tp.Dict[Asset, float] = {
            Asset(asset_name): amount for asset_name, amount in config['wallet'].items()}
        self._stats = TradingStatistics(
            price_asset=self._currency_asset,
            initial_wallet=copy(self._wallet),
            initial_balance=self.get_total_balance(),
            start_timestamp=self._ti.get_timestamp(),
            initial_coin_balance=self.get_total_coin_balance())

        self._trading_signals: tp.List[Signal] = []
        self.handlers = Handlers() \
            .add(CandlesHandler(trading_interface)) \
            .add(OrdersHandler(trading_interface))

        self._logger.info('Trading system initialized')

    def add_handler(self, handler_type: tp.Any, params: tp.Dict[str, tp.Any]) -> TradingSystemHandlerT:
        handler = handler_type(trading_interface=self._ti, **params)
        self.handlers.add(handler)
        return self.handlers[handler.get_name()]

    def stop_trading(self) -> None:
        self.cancel_all()
        self.update()

    def get_trading_statistics(self) -> TradingStatistics:
        stats = copy(self._stats)
        stats.set_hodl_result(require(self._stats.initial_coin_balance) * self._ti.get_sell_price())
        stats.set_final_wallet(self.get_wallet())
        stats.set_final_balance(self.get_total_balance())
        stats.set_finish_timestamp(self.get_timestamp())
        return stats

    def update(self) -> None:
        for handler in self.handlers.values():
            handler.update()
        for order in self.get_handler(OrdersHandler).get_new_filled_orders():
            self._handle_filled_order(order)
            self._trading_signals.append(Signal('filled_order', copy(order)))

    def get_trading_signals(self) -> tp.List[Signal]:
        signals = self._trading_signals
        self._trading_signals = []
        return signals

    def exchange_is_alive(self) -> bool:
        return self._ti.is_alive()

    def get_timestamp(self) -> int:
        return self._ti.get_timestamp()

    def create_order(self, asset_pair: AssetPair, amount: float) -> tp.Optional[Order]:
        if amount > 0:
            return self.buy(asset_pair, amount, self.get_sell_price())
        elif amount < 0:
            return self.sell(asset_pair, -amount, self.get_buy_price())
        return None

    def buy(self, asset_pair: AssetPair, amount: float, price: float) -> tp.Optional[Order]:
        if not self._risk_checker.check_order(asset_pair, price, amount, Direction.BUY, self._wallet):
            return None
        self._wallet[asset_pair.price_asset] -= price * amount
        order = self._ti.buy(asset_pair, amount, price)
        self._logger.trading(BuyEvent(asset_pair,
                                      amount,
                                      price,
                                      order.order_id))
        self.get_handler(OrdersHandler).add_new_order(copy(order))
        return order

    def sell(self, asset_pair: AssetPair, amount: float, price: float) -> tp.Optional[Order]:
        if not self._risk_checker.check_order(asset_pair, price, amount, Direction.SELL, self._wallet):
            return None
        self._wallet[asset_pair.amount_asset] -= amount
        order = self._ti.sell(asset_pair, amount, price)
        self._logger.trading(SellEvent(asset_pair,
                                       amount,
                                       price,
                                       order.order_id))
        self.get_handler(OrdersHandler).add_new_order(copy(order))
        return order

    def cancel_order(self, order: Order) -> None:
        self._ti.cancel_order(order)
        self._handle_canceled_order(order)

    def cancel_all(self) -> None:
        self._ti.cancel_all()
        active_orders = self.get_handler(OrdersHandler).get_active_orders()
        for order in active_orders:
            self._handle_canceled_order(order)

    def order_is_filled(self, order: Order) -> bool:
        return self._ti.order_is_filled(order)

    def get_price_by_direction(self, direction: Direction) -> float:
        return self.get_buy_price() if direction == Direction.BUY else self.get_sell_price()

    def get_buy_price(self) -> float:
        return self._ti.get_buy_price()

    def get_sell_price(self) -> float:
        return self._ti.get_sell_price()

    def get_active_orders(self) -> tp.Set[Order]:
        return self.get_handler(OrdersHandler).get_active_orders()

    def get_balance(self) -> float:
        balance = self._wallet[self._currency_asset]
        self._logger.info(f'Checking balance: {balance}')
        return balance

    def get_total_coin_balance(self) -> float:
        total_coins = 0.0
        for asset, amount in self._wallet.items():
            if asset != self._currency_asset:
                total_coins += amount
            else:
                if not math.isclose(require(self._ti.get_buy_price()), 0):
                    total_coins += amount / self._ti.get_buy_price()
        return total_coins

    def get_total_balance(self) -> float:
        total_balance = 0.0
        for asset, amount in self._wallet.items():
            if asset == self._currency_asset:
                total_balance += amount
            else:
                direction = Direction.from_value(-amount)
                total_balance += amount * self.get_price_by_direction(direction)
        return total_balance

    def get_wallet(self) -> tp.Dict[Asset, float]:
        self._logger.info(f'Checking wallet: {self._wallet.items()}')
        return copy(self._wallet)

    def get_last_n_candles(self, n: int) -> tp.List[Candle]:
        return self._ti.get_last_n_candles(n)

    def get_handler(self, cls: tp.Type[TradingSystemHandlerT]) \
            -> TradingSystemHandlerT:
        return self.handlers[cls.__name__]

    def _handle_canceled_order(self, order: Order) -> None:
        self.get_handler(OrdersHandler).cancel_order(order)
        if order.direction == Direction.BUY:
            self._wallet[order.asset_pair.price_asset] += order.price * order.amount
        else:  # Direction.SELL
            self._wallet[order.asset_pair.amount_asset] += order.amount
        self._logger.trading(CancelEvent(order))

    def _handle_filled_order(self, order: Order) -> None:
        if order.direction == Direction.BUY:
            self._wallet[order.asset_pair.amount_asset] += order.amount
        else:  # Direction.SELL
            self._wallet[order.asset_pair.price_asset] += order.price * order.amount
        self._stats.add_filled_order(copy(order))

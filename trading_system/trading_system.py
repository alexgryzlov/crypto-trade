from __future__ import annotations

from collections import defaultdict, OrderedDict
from copy import copy

from trading_interface.trading_interface import TradingInterface
from trading_system.candles_handler import CandlesHandler
from trading_system.trading_system_handler import TradingSystemHandler
from trading_system.trend_handler import TrendHandler
from trading_system.indicators import *
from trading_system.orders_handler import OrdersHandler

from logger.log_events import BuyEvent, SellEvent
from logger.logger import Logger

from trading import Asset, AssetPair, Signal, Order, Candle

PRICE_EPS = 0.005


class Handlers(OrderedDict):
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
    def __init__(self, trading_interface: TradingInterface):
        self.logger = Logger('TradingSystem')
        self.ti = trading_interface
        self.wallet: tp.DefaultDict[Asset, int] = defaultdict(int)
        self.trading_signals: tp.List[Signal] = []
        self.logger.info(f'Trading system TradingSystem initialized')
        self.handlers = Handlers() \
            .add(CandlesHandler(trading_interface)) \
            .add(OrdersHandler(trading_interface)) \
            .add(TrendHandler(trading_interface)) \
            .add(MovingAverageHandler(trading_interface, 25)) \
            .add(MovingAverageHandler(trading_interface, 50))

    def update(self) -> None:
        for handler in self.handlers.values():
            handler.update()
        for order in tp.cast(OrdersHandler,
                             self.handlers['OrdersHandler']
                             ).get_new_filled_orders():
            self.wallet[order.asset_pair.main_asset] -= int(
                order.direction) * order.amount
            self.trading_signals.append(Signal('filled_order', copy(order)))

    def get_trading_signals(self) -> tp.List[Signal]:
        signals = self.trading_signals
        self.trading_signals = []
        return signals

    def exchange_is_alive(self) -> bool:
        return self.ti.is_alive()

    def get_timestamp(self) -> int:
        return self.ti.get_timestamp()

    def buy(self, asset_pair: AssetPair, amount: int, price: float) -> Order:
        order = self.ti.buy(asset_pair, amount, price)
        self.logger.trading(BuyEvent(asset_pair.main_asset,
                                     asset_pair.secondary_asset,
                                     amount,
                                     price,
                                     order.order_id))
        tp.cast(OrdersHandler,
                self.handlers['OrdersHandler']).add_new_order(copy(order))
        return order

    def sell(self, asset_pair: AssetPair, amount: int, price: float) -> Order:
        order = self.ti.sell(asset_pair, amount, price)
        self.logger.trading(SellEvent(asset_pair.main_asset,
                                      asset_pair.secondary_asset,
                                      amount,
                                      price,
                                      order.order_id))
        tp.cast(OrdersHandler,
                self.handlers['OrdersHandler']).add_new_order(copy(order))
        return order

    def order_is_filled(self, order: Order) -> bool:
        return self.ti.order_is_filled(order)

    def get_buy_price(self) -> float:
        return self.ti.get_buy_price() - PRICE_EPS

    def get_sell_price(self) -> float:
        return self.ti.get_sell_price() + PRICE_EPS

    def get_active_orders(self) -> tp.List[Order]:
        return tp.cast(OrdersHandler,
                       self.handlers['OrdersHandler']).get_active_orders()

    def get_balance(self) -> float:
        balance = self.ti.get_balance()
        self.logger.info(f'Checking balance: {balance}')
        return balance

    def get_wallet(self) -> tp.DefaultDict[Asset, int]:
        self.logger.info(f'Checking wallet: {self.wallet.items()}')
        return self.wallet

    def get_last_n_candles(self, n: int) -> tp.List[Candle]:
        return self.ti.get_last_n_candles(n)

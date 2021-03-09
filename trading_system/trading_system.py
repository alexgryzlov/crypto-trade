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

from trading import AssetPair, Signal, Order

PRICE_EPS = 0.005


class Handlers(OrderedDict):
    def add(self, handler: TradingSystemHandler):
        if handler.get_name() in self.keys():
            return self

        handlers = handler.add_before()
        for i, dependent_handler in enumerate(handlers):
            if dependent_handler.get_name() in self.keys():
                handlers[i] = self[dependent_handler.get_name()]
            else:
                self[dependent_handler.get_name()] = dependent_handler
        handler.added_handlers(handlers)
        self[handler.get_name()] = handler
        return self


class TradingSystem:
    def __init__(self, trading_interface: TradingInterface):
        self.logger = Logger('TradingSystem')
        self.ti = trading_interface
        self.wallet = defaultdict(int)
        self.trading_signals = []
        self.logger.info(f'Trading system TradingSystem initialized')
        self.handlers = Handlers()\
            .add(CandlesHandler(trading_interface))\
            .add(OrdersHandler(trading_interface))\
            .add(TrendHandler(trading_interface))\
            .add(MovingAverageHandler(trading_interface, 25))\
            .add(MovingAverageHandler(trading_interface, 50))

    def update(self):
        for handler in self.handlers.values():
            handler.update()
        for order in self.handlers['OrdersHandler'].get_new_filled_orders():
            self.wallet[order.asset_pair.main_asset] -= int(order.direction) * order.amount
            self.trading_signals.append(Signal('filled_order', copy(order)))

    def get_trading_signals(self):
        signals = self.trading_signals
        self.trading_signals = []
        return signals

    def exchange_is_alive(self):
        return self.ti.is_alive()

    def get_timestamp(self):
        return self.ti.get_timestamp()

    def buy(self, asset_pair: AssetPair, amount: int, price: float):
        order = self.ti.buy(asset_pair, amount, price)
        self.logger.trading(BuyEvent(asset_pair.main_asset,
                                     asset_pair.secondary_asset,
                                     amount,
                                     price,
                                     order.order_id))
        self.handlers['OrdersHandler'].add_new_order(copy(order))
        return order

    def sell(self, asset_pair: AssetPair, amount: int, price: float):
        order = self.ti.sell(asset_pair, amount, price)
        self.logger.trading(SellEvent(asset_pair.main_asset,
                                      asset_pair.secondary_asset,
                                      amount,
                                      price,
                                      order.order_id))
        self.handlers['OrdersHandler'].add_new_order(copy(order))
        return order

    def order_is_filled(self, order: Order):
        return self.ti.order_is_filled(order)

    def get_buy_price(self):
        return self.ti.get_buy_price() - PRICE_EPS

    def get_sell_price(self):
        return self.ti.get_sell_price() + PRICE_EPS

    def get_active_orders(self):
        return self.handlers['OrdersHandler'].get_active_orders()

    def get_balance(self):
        balance = self.ti.get_balance()
        self.logger.info(f'Checking balance: {balance}')
        return balance

    def get_wallet(self):
        self.logger.info(f'Checking wallet: {self.wallet.items()}')
        return self.wallet

    def get_last_n_candles(self, n: int):
        return self.ti.get_last_n_candles(n)

from collections import defaultdict, OrderedDict
from copy import copy

from trading_interface.trading_interface import TradingInterface
from trading_system.candles_handler import CandlesHandler
from trading_system.trading_system_handler import TradingSystemHandler
from trading_system.trend_handler import TrendHandler
from trading_system.indicators import *
from trading_system.orders_handler import OrdersHandler

from trading_system.trading_statistics import TradingStatistics

from logger.log_events import BuyEvent, SellEvent, CancelEvent
from logger.logger import Logger

from trading import Asset, AssetPair, Signal, Order

PRICE_EPS = 0.005


class Handlers(OrderedDict):
    def add(self, handler: TradingSystemHandler):
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
    def __init__(self, trading_interface: TradingInterface, config: tp.Dict[str, tp.Any]):
        self.logger = Logger('TradingSystem')
        self.ti = trading_interface
        self.stats = TradingStatistics(self.ti.get_balance())
        self.wallet = defaultdict(int)
        self.currency_asset = Asset(config['currency_asset'])
        self.trading_signals = []
        self.handlers = Handlers() \
            .add(CandlesHandler(trading_interface)) \
            .add(OrdersHandler(trading_interface)) \
            .add(TrendHandler(trading_interface)) \
            .add(MovingAverageHandler(trading_interface, 25)) \
            .add(MovingAverageHandler(trading_interface, 50))
        self.logger.info('Trading system initialized')

    def stop_trading(self) -> None:
        for asset, amount in self.wallet.items():
            self.create_order(asset_pair=AssetPair(asset, self.currency_asset),
                              amount=-amount)
        self.cancel_all()

    def get_trading_statistics(self) -> TradingStatistics:
        self.stats.set_final_balance(self.get_balance())
        return copy(self.stats)

    def update(self):
        for handler in self.handlers.values():
            handler.update()
        for order in self.handlers['OrdersHandler'].get_new_filled_orders():
            self.stats.add_filled_order(copy(order))
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

    def create_order(self, asset_pair: AssetPair, amount: int) -> tp.Optional[Order]:
        if amount > 0:
            return self.buy(asset_pair, amount, self.get_sell_price())
        elif amount < 0:
            return self.sell(asset_pair, -amount, self.get_buy_price())
        return None

    def buy(self, asset_pair: AssetPair, amount: int, price: float) -> Order:
        order = self.ti.buy(asset_pair, amount, price)
        self.logger.trading(BuyEvent(asset_pair.main_asset,
                                     asset_pair.secondary_asset,
                                     amount,
                                     price,
                                     order.order_id))
        self.handlers['OrdersHandler'].add_new_order(copy(order))
        return order

    def sell(self, asset_pair: AssetPair, amount: int, price: float) -> Order:
        order = self.ti.sell(asset_pair, amount, price)
        self.logger.trading(SellEvent(asset_pair.main_asset,
                                      asset_pair.secondary_asset,
                                      amount,
                                      price,
                                      order.order_id))
        self.handlers['OrdersHandler'].add_new_order(copy(order))
        return order

    def cancel_order(self, order: Order):
        self.ti.cancel_order(order)
        self.logger.trading(CancelEvent(order))
        self.handlers['OrdersHandler'].cancel_order(order)

    def cancel_all(self):
        self.ti.cancel_all()
        for order in self.handlers['OrdersHandler'].get_active_orders():
            self.logger.trading(CancelEvent(order))
        self.handlers['OrdersHandler'].cancel_all()

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

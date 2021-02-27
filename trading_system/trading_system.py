from collections import defaultdict

from trading_interface.trading_interface import TradingInterface
from trading_system.candles_handler import CandlesHandler
from trading_system.trend_handler import TrendHandler
from trading_system.moving_average_handler import MovingAverageHandler

from logger.log_events import BuyEvent, SellEvent, FilledOrderEvent
from logger import logger

from trading.asset import AssetPair
from trading.order import Order

PRICE_EPS = 0.005


class TradingSystem:
    def __init__(self, trading_interface: TradingInterface):
        self.logger = logger.get_logger('TradingSystem')
        self.ti = trading_interface
        self.active_orders = []
        self.wallet = defaultdict(int)
        self.logger.info(f'Trading system TradingSystem initialized')
        self.handlers = {
            'CandlesHandler': CandlesHandler(trading_interface),
            'TrendHandler': TrendHandler(trading_interface),
            'MovingAverageHandler25': MovingAverageHandler(trading_interface, 25),
            'MovingAverageHandler50': MovingAverageHandler(trading_interface, 50)
        }

    def update(self):
        self.__check_active_orders()
        for handler in self.handlers.values():
            handler.update()

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
        self.active_orders.append(order)
        return order

    def sell(self, asset_pair: AssetPair, amount: int, price: float):
        order = self.ti.sell(asset_pair, amount, price)
        self.logger.trading(SellEvent(asset_pair.main_asset,
                                      asset_pair.secondary_asset,
                                      amount,
                                      price,
                                      order.order_id))
        self.active_orders.append(order)
        return order

    def order_is_filled(self, order: Order):
        order_filled = self.ti.order_is_filled(order)
        return order_filled

    def get_buy_price(self):
        return self.ti.get_buy_price() - PRICE_EPS

    def get_sell_price(self):
        return self.ti.get_sell_price() + PRICE_EPS

    def get_active_orders(self):
        return self.active_orders

    def get_balance(self):
        balance = self.ti.get_balance()
        self.logger.info(f'Checking balance: {balance}')
        return balance

    def get_wallet(self):
        self.logger.info(f'Checking wallet: {self.wallet.items()}')
        return self.wallet

    def get_last_n_candles(self, n: int):
        return self.ti.get_last_n_candles(n)

    def __check_active_orders(self):
        filled_orders = [order for order in self.active_orders if self.order_is_filled(order)]
        for order in filled_orders:
            self.logger.trading(FilledOrderEvent(order.order_id))
            self.wallet[order.asset_pair.a1] -= int(order.direction) * order.amount
        self.active_orders = [order for order in self.active_orders if not self.order_is_filled(order)]

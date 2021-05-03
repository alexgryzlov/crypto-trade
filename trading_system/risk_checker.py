import typing as tp

from logger.logger import Logger
from helpers.typing.common_types import Config

from trading_interface.trading_interface import TradingInterface

from trading import Order, Asset, Timeframe, Timestamp


class RiskChecker:
    def __init__(self, trading_interface: TradingInterface, config: Config):
        self._logger = Logger('RiskChecker')
        self._ti = trading_interface
        self._max_order_amount = config["max_order_amount"]
        self._max_order_price = config["max_order_price"]
        self._available_assets = [Asset(asset_name) for asset_name in config["available_assets"]]
        self._max_order_count_per_period = config["max_order_count_per_period"]
        self._rejection_period = Timeframe(config["rejection_period"])
        self._accepted_orders_ts: tp.List[int] = []

    def check(self, order: Order) -> bool:
        while self._accepted_orders_ts and \
                self._accepted_orders_ts[0] + self._rejection_period.to_seconds() < self._ti.get_timestamp():
            self._accepted_orders_ts = self._accepted_orders_ts[1:]

        if order.amount > self._max_order_amount:
            self._logger.warning(f"{order} rejected, large order amount")
            return False

        if order.asset_pair.amount_asset not in self._available_assets:
            self._logger.warning(f"{order} rejected, forbidden amount asset")
            return False

        if order.asset_pair.price_asset not in self._available_assets:
            self._logger.warning(f"{order} rejected, forbidden price asset")
            return False

        if order.price > self._max_order_price:
            self._logger.warning(f"{order} rejected, large order price")
            return False

        if len(self._accepted_orders_ts) + 1 > self._max_order_count_per_period:
            self._logger.warning(f"{order} rejected, many orders per period")
            return False

        self._accepted_orders_ts.append(self._ti.get_timestamp())
        return True

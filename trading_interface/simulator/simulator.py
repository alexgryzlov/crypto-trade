import datetime
import typing as tp
from copy import copy

from trading_interface.simulator.clock_simulator import ClockSimulator
from trading_interface.trading_interface import TradingInterface
from market_data_api.market_data_downloader import MarketDataDownloader

from trading import Order, Direction, AssetPair, TimeRange, Candle
from trading_interface.simulator.price_simulator import PriceSimulator, PriceSimulatorType


class Simulator(TradingInterface):
    def __init__(self,
                 asset_pair: AssetPair,
                 time_range: TimeRange,
                 clock: ClockSimulator,
                 config: tp.Dict[str, tp.Any],
                 price_simulation_type: PriceSimulatorType = PriceSimulatorType.ThreeIntervalPath):
        ts_offset = int(datetime.timedelta(days=1).total_seconds())
        self.candles = MarketDataDownloader().get_candles(
            asset_pair, clock.get_timeframe(), TimeRange(time_range.from_ts - ts_offset, time_range.to_ts))
        self.clock = clock
        self.candle_index_offset = ts_offset // clock.get_seconds_per_candle()
        self.active_orders: tp.Set[Order] = set()
        self.last_used_order_id = 0
        self.filled_order_ids: tp.Set[int] = set()
        self.balance = float(config['initial_balance'])
        self.price_shift = float(config['price_shift'])
        self.price_simulator = PriceSimulator(self.clock.candles_lifetime, price_simulation_type)

    def is_alive(self) -> bool:
        self.__fill_orders()
        self.clock.next_iteration()
        return self.__get_current_candle_index(truncated_index=False) < len(self.candles)

    def stop_trading(self) -> None:
        self.__fill_orders()

    def get_timestamp(self) -> int:
        return self.clock.get_timestamp()

    def get_balance(self) -> float:
        return self.balance

    def buy(self, asset_pair: AssetPair, amount: float, price: float) -> Order:
        order = Order(order_id=self.__get_new_order_id(),
                      asset_pair=asset_pair,
                      amount=amount,
                      price=price,
                      direction=Direction.BUY)
        self.active_orders.add(copy(order))
        return order

    def sell(self, asset_pair: AssetPair, amount: float, price: float) -> Order:
        order = Order(order_id=self.__get_new_order_id(),
                      asset_pair=asset_pair,
                      amount=amount,
                      price=price,
                      direction=Direction.SELL)
        self.active_orders.add(copy(order))
        return order

    def cancel_order(self, order: Order) -> None:
        self.active_orders.discard(order)

    def cancel_all(self) -> None:
        self.active_orders.clear()

    def order_is_filled(self, order: Order) -> bool:
        return order.order_id in self.filled_order_ids

    def get_sell_price(self) -> float:
        return self.__get_current_price() * (1 + self.price_shift)

    def get_buy_price(self) -> float:
        return self.__get_current_price() * (1 - self.price_shift)

    def get_last_n_candles(self, n: int) -> tp.List[Candle]:
        candle_index = self.__get_current_candle_index()
        return self.candles[max(0, candle_index - n): candle_index]

    def get_orderbook(self):  # type: ignore
        pass

    def __order_is_filled(self, order: Order) -> bool:
        return (order.direction == Direction.BUY and
                order.price > self.get_sell_price()) or \
               (order.direction == Direction.SELL and
                order.price < self.get_buy_price())

    def __fill_orders(self) -> None:
        filled_orders = set(filter(self.__order_is_filled, self.active_orders))
        self.active_orders = set(
            filter(lambda order: not self.__order_is_filled(order),
                   self.active_orders))
        for order in filled_orders:
            self.filled_order_ids.add(order.order_id)
            self.balance += int(order.direction) * order.price * order.amount

    def __get_current_price(self) -> float:
        candle = self.candles[self.__get_current_candle_index()]
        return self.price_simulator.get_price(
            candle, self.clock.get_current_candle_lifetime())

    def __get_current_candle_index(self, truncated_index: bool = True) -> int:
        index = self.candle_index_offset + self.clock.get_iterated_candles_count()
        if not truncated_index:
            return index
        return min(index, len(self.candles) - 1)

    def __get_new_order_id(self) -> int:
        self.last_used_order_id += 1
        return self.last_used_order_id

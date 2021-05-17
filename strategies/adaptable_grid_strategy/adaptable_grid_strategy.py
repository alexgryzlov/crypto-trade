import numpy as np

import trading_system.trading_system as ts
from helpers.typing.common_types import Config
from strategies.grid_strategy.grid_strategy import GridStrategy
from trading import Order
import typing as tp
from itertools import chain


class AdaptableGridStrategy(GridStrategy):  # type: ignore
    def __init__(self, config: Config) -> None:
        super().__init__(config)
        self.threshold = config['threshold']
        self.window = config['window']
        self.coef = config['coef']
        self.timeout = config['timeout_in_candles'] * config['candles_lifetime']
        self.timeout_only = config['timeout_only']
        self.handle_filled_orders = config['handle_filled_orders']
        self.ticks = 0

    def calculate_base_price(self) -> float:
        opens_and_closes = np.array(list(chain(
            *self.__get_last_n_opens_and_closes())))
        return 1.005 * np.median(opens_and_closes)

    def calculate_interval(self) -> float:
        opens_and_closes = np.array(list(chain(
            *self.__get_last_n_opens_and_closes())))
        #print(self.coef * opens_and_closes.std())
        return self.coef * opens_and_closes.std()

    def init_trading(self, trading_system: ts.TradingSystem) -> None:
        self.ts = trading_system
        # not placing orders at the start
        # waiting for enough candles to calculate mean and variance

    def update(self) -> None:
        new_interval = self.calculate_interval()
        new_base = self.calculate_base_price()
        condition = self.ticks > self.timeout or (
            not self.timeout_only and (
                self.__rel_diff(new_base, self.base_price) >  # type: ignore
                self.threshold))
        if condition:
            self.logger.info(f'Updating grid: new base price = {new_base}, '
                             f'new interval = {new_interval}')
            self.base_price = new_base
            self.interval = new_interval
            self.ts.cancel_all()
            self.place_orders()
            self.ticks = 0
        self.ticks += 1

    def handle_filled_order_signal(self, order: Order) -> None:
        if self.handle_filled_orders:
            super().handle_filled_order_signal(order)

    def __get_last_n_opens_and_closes(self) -> tp.List[tp.Tuple[float]]:
        return [(candle.open, candle.close) for candle in
            self.ts.ti.get_last_n_candles(self.window)]

    def __get_last_n_mid_prices(self) -> np.array:
        return np.array(list(
            map(lambda x: x.get_mid_price(),
                self.ts.ti.get_last_n_candles(self.window))))

    def __rel_diff(self, a: float, b: float) -> float:
        return abs(a - b) / b

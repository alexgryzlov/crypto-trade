import numpy as np

from helpers.typing.common_types import Config
from strategies.grid_strategy.grid_strategy import GridStrategy
from trading import Order


class AdaptableGridStrategy(GridStrategy):  # type: ignore
    def __init__(self, config: Config) -> None:
        super().__init__(config)
        self.threshold = config['threshold']
        self.window = config['window']
        self.coef = config['coef']

    def calculate_base_price(self) -> float:
        return self.__get_last_n_mid_prices().mean()

    def calculate_interval(self) -> float:
        return (self.coef * self.__get_last_n_mid_prices().std() /
                self.base_level)

    def update(self) -> None:
        new_interval = self.calculate_interval()
        new_base = self.calculate_base_price()
        if (self.__rel_diff(new_interval, self.interval) >  # type: ignore
                self.threshold or
                self.__rel_diff(new_base, self.base_price) >  # type: ignore
                self.threshold):
            self.logger.info(f'Updating grid: new base price = {new_base}, '
                             f'new interval = {new_interval}')
            self.base_price = new_base
            self.interval = new_interval
            self.ts.cancel_all()
            self.place_orders()

    def handle_filled_order_signal(self, order: Order) -> None:
        pass

    def __get_last_n_mid_prices(self) -> np.array:
        return np.array(list(
            map(lambda x: x.get_mid_price(),
                self.ts.ti.get_last_n_candles(self.window))))

    def __rel_diff(self, a: float, b: float) -> float:
        return abs(a - b) / b

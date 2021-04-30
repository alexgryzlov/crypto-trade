import typing as tp
from abc import ABC, abstractmethod

from trading import AssetPair, Order, Candle


class TradingInterface(ABC):
    @abstractmethod
    def is_alive(self) -> bool:
        pass

    @abstractmethod
    def stop_trading(self) -> None:
        pass

    @abstractmethod
    def get_timestamp(self) -> int:
        pass

    @abstractmethod
    def buy(self, amount: float, price: float) -> tp.Optional[Order]:
        pass

    @abstractmethod
    def sell(self, amount: float, price: float) -> tp.Optional[Order]:
        pass

    @abstractmethod
    def cancel_order(self, order: Order) -> None:
        pass

    @abstractmethod
    def cancel_all(self) -> None:
        pass

    @abstractmethod
    def order_is_filled(self, order: Order) -> bool:
        pass

    @abstractmethod
    def get_buy_price(self) -> float:
        pass

    @abstractmethod
    def get_sell_price(self) -> float:
        pass

    @abstractmethod
    def get_orderbook(self):  # type: ignore
        pass

    @abstractmethod
    def get_last_n_candles(self, n: int) -> tp.List[Candle]:
        pass

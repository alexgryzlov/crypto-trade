from trading import AssetPair, Order, Candle
import typing as tp
from abc import ABC, abstractmethod


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
    def get_balance(self) -> float:
        pass

    @abstractmethod
    def buy(self, asset_pair: AssetPair, amount: float, price: float) -> Order:
        pass

    @abstractmethod
    def sell(self, asset_pair: AssetPair, amount: float, price: float) -> Order:
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

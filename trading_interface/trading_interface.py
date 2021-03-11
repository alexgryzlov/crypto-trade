from trading import AssetPair, Order, Candle
import typing as tp


class TradingInterface:
    def is_alive(self) -> bool:
        pass

    def get_timestamp(self) -> int:
        pass

    def get_balance(self) -> float:
        pass

    def buy(self, asset_pair: AssetPair, amount: int, price: float) -> Order:
        pass

    def sell(self, asset_pair: AssetPair, amount: int, price: float) -> Order:
        pass

    def cancel_order(self, order: Order) -> bool:
        pass

    def cancel_all(self) -> None:
        pass

    def order_is_filled(self, order: Order) -> bool:
        pass

    def get_buy_price(self) -> float:
        pass

    def get_sell_price(self) -> float:
        pass

    def get_orderbook(self):  # type: ignore
        pass

    def get_last_n_candles(self, n: int) -> tp.List[Candle]:
        pass

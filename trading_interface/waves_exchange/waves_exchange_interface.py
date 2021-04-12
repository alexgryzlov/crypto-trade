import ccxt
import typing as tp
from abc import ABC, abstractmethod

from trading import AssetPair, Order, Candle
from trading_interface.trading_interface import TradingInterface

from helpers.typing.common_types import Config


class WAVESExchangeInterface(TradingInterface):
    def __init__(self, config: Config):
        self._exchange = ccxt.wavesexchange()
        self.asset_pair = AssetPair(*config['asset_pair'])
        # MarketDataDownloader._Exchange.load_markets()

    def is_alive(self) -> bool:
        return self._exchange.fetchStatus()['status'] == 'ok'

    def stop_trading(self) -> None:
        pass

    def get_timestamp(self) -> int:
        pass

    def buy(self, asset_pair: AssetPair, amount: float, price: float) -> Order:
        pass

    def sell(self, asset_pair: AssetPair, amount: float, price: float) -> Order:
        pass

    def cancel_order(self, order: Order) -> None:
        pass

    def cancel_all(self) -> None:
        pass

    def order_is_filled(self, order: Order) -> bool:
        pass

    def get_buy_price(self) -> float:
        return self.get_orderbook()['bids'][0][0]

    def get_sell_price(self) -> float:
        return self.get_orderbook()['asks'][0][0]

    def get_orderbook(self):  # type: ignore
        return self._exchange.fetch_order_book(str(reversed(self.asset_pair)))

    def get_last_n_candles(self, n: int) -> tp.List[Candle]:
        pass

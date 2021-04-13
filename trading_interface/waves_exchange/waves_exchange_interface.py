import requests
import typing as tp
from retry import retry

from trading import AssetPair, Order, Candle
from trading_interface.trading_interface import TradingInterface

from helpers.typing.common_types import Config


class WAVESExchangeInterface(TradingInterface):
    def __init__(self, trading_config: Config, exchange_config: Config):
        self.asset_pair = AssetPair(*trading_config['asset_pair'])
        self._host = 'https://matcher-testnet.waves.exchange'  # exchange_config['matcher']

    def is_alive(self) -> bool:
        # return self._exchange.fetchStatus()['status'] == 'ok'
        return True

    def stop_trading(self) -> None:
        pass

    def get_timestamp(self) -> int:
        pass

    def buy(self, amount: float, price: float) -> Order:
        return self._exchange.createLimitBuyOrder(
            symbol=str(self.asset_pair),
            amount=amount,
            price=price)

    def sell(self, amount: float, price: float) -> Order:
        return self._exchange.createLimitSellOrder(
            symbol=str(self.asset_pair),
            amount=amount,
            price=price)

    def cancel_order(self, order: Order) -> None:
        pass

    def cancel_all(self) -> None:
        pass

    def order_is_filled(self, order: Order) -> bool:
        pass

    def get_buy_price(self) -> float:
        return self.get_orderbook()['bids'][0]['price']

    def get_sell_price(self) -> float:
        return self.get_orderbook()['asks'][0]['price']

    def get_orderbook(self):  # type: ignore
        return self._request(f'orderbook/{str(self.asset_pair)}')

    def get_last_n_candles(self, n: int) -> tp.List[Candle]:
        pass

    @retry(RuntimeError, tries=3, delay=1)
    def _request(self, api_request: str, **request_params) -> tp.Any:
        response = requests.get(
            f'{self._host}/matcher/{api_request}',
            params=request_params)
        if not response:
            raise RuntimeError(response.content)
        return response.json()

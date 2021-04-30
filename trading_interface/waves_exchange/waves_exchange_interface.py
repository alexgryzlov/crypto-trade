import requests
import typing as tp
from retry import retry

from trading import Asset, AssetPair, Order, Candle, Direction
from trading_interface.trading_interface import TradingInterface

from helpers.typing.common_types import Config
from axolotl_curve25519 import calculateSignature
from time import time
from os import urandom
from base58 import b58decode, b58encode
from struct import pack
import json
from logger.logger import Logger


class WAVESExchangeInterface(TradingInterface):
    def __init__(self, trading_config: Config, exchange_config: Config):
        self.logger = Logger("TestnetInterface")
        self.asset_pair = AssetPair(*trading_config['asset_pair'])
        self._host = exchange_config['matcher']
        self._matcher_public_key = bytes(self._request('get', ""), 'utf-8')
        self._matcher_fee = exchange_config['matcher_fee']  # default - 0.003 waves
        self._price_shift = exchange_config['price_shift']
        self._max_lifetime = exchange_config['max_lifetime']
        self._private_key = bytes(exchange_config["private_key"], 'utf-8')
        self._public_key = bytes(exchange_config["public_key"], 'utf-8')
        self._version = exchange_config['version']

    def is_alive(self) -> bool:
        # return self._exchange.fetchStatus()['status'] == 'ok'
        return True

    def stop_trading(self) -> None:
        pass

    def get_timestamp(self) -> int:
        pass

    def buy(self, amount: float, price: float) -> tp.Optional[Order]:
        return self._place_order(0, amount, price)

    def sell(self, amount: float, price: float) -> tp.Optional[Order]:
        return self._place_order(1, amount, price)

    def cancel_order(self, order: Order) -> None:
        signature_data = b58decode(self._public_key) + b58decode(order.order_id)
        signature = self._sign(signature_data)
        data = json.dumps({
            "sender": self._public_key.decode("utf-8"),
            "orderId": order.order_id,
            "signature": signature
        })
        response = self._request('post', f'orderbook/{str(self.asset_pair)}/cancel',
                                 body=data).json()
        if response['status'] != 'OrderCancelled':
            self.logger.warning(f"Order is not cancelled. Status: {response['status']}")

    def cancel_all(self) -> None:
        pass

    def order_is_filled(self, order: Order) -> bool:
        pass

    def get_buy_price(self) -> float:
        return self.get_orderbook()['bids'][0]['price']

    def get_sell_price(self) -> float:
        return self.get_orderbook()['asks'][0]['price']

    def get_orderbook(self):  # type: ignore
        return self._request('get', f'orderbook/{str(self.asset_pair)}')

    def get_last_n_candles(self, n: int) -> tp.List[Candle]:
        pass

    @retry(RuntimeError, tries=3, delay=1)
    def _request(self, request_type: str, api_request: str, body='', **request_params) -> tp.Any:
        if request_type == "post":
            response = requests.post(
                f'{self._host}/matcher/{api_request}',
                data=body,
                headers={'content-type': 'application/json'},
                params=request_params
            )
        else:
            response = requests.get(
                f'{self._host}/matcher/{api_request}',
                params=request_params
            )
        if not response:
            raise RuntimeError(response.content)
        return response.json()

    def _place_order(self, optype: int, amount: float, price: float) -> tp.Optional[Order]:
        scaled_price = int(price * self._price_shift)
        scaled_amount = int(amount * self._price_shift)
        timestamp = int(time() * 1000)
        expiration = timestamp + self._max_lifetime * 1000
        signature_data = pack("B", self._version) + \
                         b58decode(self._public_key) + \
                         b58decode(self._matcher_public_key) + \
                         self._serialize_asset_id(self.asset_pair.amount_asset) + \
                         self._serialize_asset_id(self.asset_pair.price_asset) + \
                         pack("B", optype) + \
                         pack(">Q", scaled_price) + \
                         pack(">Q", scaled_amount) + \
                         pack(">Q", timestamp) + \
                         pack(">Q", expiration) + \
                         pack(">Q", self._matcher_fee) + \
                         b'\0'

        signature = self._sign(signature_data)
        order_direction = "sell" if optype == 1 else "buy"
        data = json.dumps({
            "senderPublicKey": self._public_key.decode("utf-8"),
            "matcherPublicKey": self._matcher_public_key.decode("utf-8"),
            "assetPair": {
                "amountAsset": str(self.asset_pair.amount_asset),
                "priceAsset": str(self.asset_pair.price_asset),
            },
            "orderType": order_direction,
            "price": scaled_price,
            "amount": scaled_amount,
            "timestamp": timestamp,
            "expiration": expiration,
            "matcherFee": self._matcher_fee,
            "signature": signature,
            "version": self._version
        })
        response = self._request('post', 'orderbook', body=data)
        if response['status'] != "OrderAccepted":
            self.logger.warning(f"Order is not accepted. Status: {response['status']}")
            return None

        return Order(order_id=response['message']['id'],
                     asset_pair=self.asset_pair,
                     amount=amount,
                     price=price,
                     direction=Direction.from_string(order_direction))

    @staticmethod
    def _serialize_asset_id(asset: Asset):
        return b'\1' + b58decode(str(asset)) if str(asset) != "WAVES" else b'\0'

    def _sign(self, data):
        return b58encode(calculateSignature(urandom(64),
                                            b58decode(self._private_key), data))

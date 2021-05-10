import requests
import typing as tp
from retry import retry

from trading import Asset, AssetPair, Order, Candle, Direction, Timeframe, TimeRange
from trading_interface.trading_interface import TradingInterface
from market_data_api.market_data_downloader import MarketDataDownloader

from helpers.typing.common_types import Config
from axolotl_curve25519 import calculateSignature
from time import time
from os import urandom
from base58 import b58decode, b58encode
from struct import pack
import json
from logger.logger import Logger

# Where to put it?
exchange_assets = {'WAVES': 'WAVES',
                   'BTC': 'DWgwcZTMhSvnyYCoWLRUXXSH1RSkzThXLJhww9gwkqdn'}


def to_waves_format(asset_pair: AssetPair) -> AssetPair:
    return AssetPair.from_string(exchange_assets[str(asset_pair.amount_asset)],
                                 exchange_assets[str(asset_pair.price_asset)])


class WAVESExchangeInterface(TradingInterface):
    def __init__(self, trading_config: Config, exchange_config: Config):
        self.logger = Logger("TestnetInterface")
        self.asset_pair_human_readable = AssetPair.from_string(*trading_config['asset_pair'])
        self.asset_pair = to_waves_format(self.asset_pair_human_readable)
        self._host: str = exchange_config['matcher']
        self._matcher_public_key = bytes(self._request('get', ""), 'utf-8')
        self._matcher_fee: int = exchange_config['matcher_fee']  # default - 0.003 waves
        self._price_shift: int = exchange_config['price_shift']
        self._max_lifetime: int = exchange_config['max_lifetime']
        self._private_key = bytes(exchange_config["private_key"], 'utf-8')
        self._public_key = bytes(exchange_config["public_key"], 'utf-8')
        self._version: int = exchange_config['version']
        self._active_orders: tp.Set[Order] = set()
        self._filled_order_ids: tp.Set[str] = set()
        self._cancelled_orders_ids: tp.Set[str] = set()
        self._candles: tp.List[Candle] = []

        self._timeframe = Timeframe(trading_config['timeframe'])  # TODO: This should be inside clock

        # // 1000 for MarketDataDownloader
        # 'before_start_offset' probably should not be inside exchange_config (TODO: add clock config)
        self._last_candle_fetch = self.get_timestamp() // 1000 - exchange_config['before_start_offset']

        self._fetch_orders()
        self._fetch_candles()

    def is_alive(self) -> bool:
        return len(self._request("get", "")) != 0

    def stop_trading(self) -> None:
        pass

    def get_timestamp(self) -> int:
        # TODO: WavesEX time -> time()*1000
        #       DataDownloader -> time()
        #       Need ExchangeClock class to provide both times
        return int(time() * 1000)

    def buy(self, amount: float, price: float) -> tp.Optional[Order]:
        return self._place_order(Direction.BUY, amount, price)

    def sell(self, amount: float, price: float) -> tp.Optional[Order]:
        return self._place_order(Direction.SELL, amount, price)

    def cancel_order(self, order: Order) -> bool:
        signature_data: bytes = b58decode(self._public_key) + b58decode(order.order_id)
        signature: str = self._sign(signature_data)
        data: str = json.dumps({
            "sender": self._public_key.decode("utf-8"),
            "orderId": order.order_id,
            "signature": signature
        })
        response = self._request('post', f'orderbook/{str(self.asset_pair)}/cancel',
                                 body=data)
        if response['status'] != 'OrderCanceled':
            self.logger.warning(f"Order is not cancelled. Status: {response['status']}")
            return False
        self._active_orders.discard(order)
        self._cancelled_orders_ids.add(order.order_id)
        return True

    def cancel_all(self) -> None:
        self._fetch_orders()
        response = self._try_cancel_all()
        while response['status'] != 'BatchCancelCompleted':
            self.logger.warning(f"Failed to cancel all orders, retrying. Status: {response['status']}")
            response = self._try_cancel_all()
        self._cancelled_orders_ids |= self._active_orders
        self._active_orders.clear()

    def _try_cancel_all(self) -> tp.Any:
        timestamp = self.get_timestamp()
        signature_data: bytes = b58decode(self._public_key) + pack(">Q", timestamp)
        signature: str = self._sign(signature_data)
        data: str = json.dumps({
            "sender": self._public_key.decode("utf-8"),
            "timestamp": timestamp,
            "signature": signature
        })
        return self._request('post', f'orderbook/cancel', body=data)

    def order_is_filled(self, order: Order) -> bool:
        if order.order_id in self._filled_order_ids:
            return True
        self._fetch_orders()
        return order.order_id in self._filled_order_ids

    def get_buy_price(self) -> float:
        return self.get_orderbook()['bids'][0]['price']

    def get_sell_price(self) -> float:
        return self.get_orderbook()['asks'][0]['price']

    def get_orderbook(self):  # type: ignore
        return self._request('get', f'orderbook/{str(self.asset_pair)}')

    def get_last_n_candles(self, n: int) -> tp.List[Candle]:
        self._fetch_candles()
        return self._candles[-n:]

    @retry(RuntimeError, tries=3, delay=1)
    def _request(self, request_type: str, api_request: str, body: str = '',
                 headers: tp.Optional[dict] = None, params: tp.Optional[dict] = None) -> tp.Any:
        if headers is None:
            headers = {'content-type': 'application/json'}
        if request_type == "post":
            response = requests.post(
                f'{self._host}/matcher/{api_request}',
                data=body,
                headers=headers,
                params=params
            )
        elif request_type == "get":
            response = requests.get(
                f'{self._host}/matcher/{api_request}',
                data=body,
                headers=headers,
                params=params
            )
        else:
            raise ValueError(f"Unknown request type: {request_type}")
        return response.json()

    def _place_order(self, direction: Direction, amount: float, price: float) -> tp.Optional[Order]:
        scaled_price = int(price * self._price_shift)
        scaled_amount = int(amount * self._price_shift)
        timestamp = self.get_timestamp()
        expiration = timestamp + self._max_lifetime * 1000
        optype: int = 0 if direction == Direction.BUY else 1
        # https://docs.waves.exchange/en/waves-matcher/matcher-api
        signature_data: bytes = pack("B", self._version) + \
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
        signature: str = self._sign(signature_data)
        order_direction: str = "buy" if direction == Direction.BUY else "sell"
        data: str = json.dumps({
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

        order = Order(order_id=response['message']['id'],
                      asset_pair=self.asset_pair,
                      amount=amount,
                      price=price,
                      direction=Direction.from_string(order_direction))
        self._active_orders.add(order)
        return order

    @staticmethod
    def _serialize_asset_id(asset: Asset) -> bytes:
        return b'\1' + b58decode(str(asset)) if str(asset) != "WAVES" else b'\0'

    def _sign(self, data: bytes) -> str:
        return b58encode(calculateSignature(urandom(64),
                                            b58decode(self._private_key), data)).decode('ascii')

    def _fetch_orders(self, active: bool = False,
                      cancelled: bool = False,
                      filled: bool = False) -> None:
        """
        Updates self.active_orders, self.cancelled_orders and self.filled_orders
        Fetches all types of orders by default (everything False)
        If active is True and cancelled or filled is True, request will return nothing
        """
        fetch_all: bool = not active and not cancelled and not filled
        timestamp = self.get_timestamp()
        signature_data: bytes = b58decode(self._public_key) + \
                                pack(">Q", timestamp)
        signature: str = self._sign(signature_data)
        headers: dict = {
            "accept": "application/json",
            "Timestamp": str(timestamp),
            "Signature": signature
        }
        url_params: dict = {
            "activeOnly": active,
            "closedOnly": cancelled | filled,
        }
        response = self._request('get', f'orderbook/{self._public_key.decode("utf-8")}',
                                 headers=headers, params=url_params)
        # I'm not sure how to handle the case of 500 or 503 here (or what to do with that in _request)
        # This is only "happy path" (or if 500/503 is json-able then it will do nothing)
        for params in response:
            order = Order(order_id=params['id'],
                          asset_pair=AssetPair(Asset(params['assetPair']['amountAsset']),
                                               Asset(params['assetPair']['priceAsset'])),
                          price=int(params['price'] / self._price_shift),
                          amount=int(params['amount'] / self._price_shift),
                          direction=Direction.from_string(params['type']))
            if params['status'] == 'Accepted' and (fetch_all or active):
                self._active_orders.add(order)
            elif params['status'] == 'Cancelled' and (fetch_all or cancelled):
                self._cancelled_orders_ids.add(order.order_id)
            elif params['status'] == 'Filled' and (fetch_all or filled):
                self._active_orders.discard(order)
                self._filled_order_ids.add(order.order_id)

    def _fetch_candles(self) -> None:
        timestamp = self.get_timestamp() // 1000
        new_candles = MarketDataDownloader.get_candles(self.asset_pair_human_readable, self._timeframe,
                                                       TimeRange(self._last_candle_fetch, timestamp))
        self._last_candle_fetch = timestamp
        self._candles.extend(new_candles)
        # TODO: may be use collections.deque(max_len=const) for candles

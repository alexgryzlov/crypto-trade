import requests
import typing as tp
from retry import retry

from trading import Asset, AssetPair, Order, Candle, Direction, Timeframe, TimeRange
from trading_interface.trading_interface import TradingInterface
from market_data_api.market_data_downloader import MarketDataDownloader
from trading_interface.waves_exchange.waves_exchange_clock import WAVESExchangeClock

from helpers.typing.common_types import Config
from axolotl_curve25519 import calculateSignature
from os import urandom
from base58 import b58decode, b58encode
from struct import pack
import json
from logger.logger import Logger


class WAVESExchangeInterface(TradingInterface):
    def __init__(self, trading_config: Config, exchange_config: Config):
        self.logger = Logger("TestnetInterface")
        self._asset_translation: tp.Dict[str, str] = exchange_config['asset_translation']
        self.asset_pair_human_readable = AssetPair.from_string(*trading_config['asset_pair'])
        self.asset_pair = self._to_waves_format(self.asset_pair_human_readable)
        self._host: str = exchange_config['matcher']
        self._matcher_public_key = bytes(self._request('get', ""), 'utf-8')
        self._matcher_fee: int = exchange_config['matcher_fee']  # default - 0.003 waves
        self._fee_currency = Asset(exchange_config['fee_currency'])
        self._decimals: tp.Dict[str, int] = exchange_config['decimals']
        self._max_lifetime: int = exchange_config['max_lifetime']
        self._private_key = bytes(trading_config["private_key"], 'utf-8')
        self._public_key = bytes(trading_config["public_key"], 'utf-8')
        self._version: int = exchange_config['version']
        self._active_orders: tp.Set[Order] = set()
        self._filled_order_ids: tp.Set[str] = set()
        self._cancelled_orders_ids: tp.Set[str] = set()
        self._candles: tp.List[Candle] = []
        self._candles_lifetime = Timeframe(trading_config['timeframe'])
        self._clock = WAVESExchangeClock(exchange_config['clock'])

        self._fetch_orders()
        self._fetch_candles()

    def _to_waves_format(self, asset_pair: AssetPair) -> AssetPair:
        return AssetPair.from_string(self._asset_translation[str(asset_pair.amount_asset)],
                                     self._asset_translation[str(asset_pair.price_asset)])

    def is_alive(self) -> bool:
        return len(self._request("get", "")) != 0

    def stop_trading(self) -> None:
        self.cancel_all()

    def get_clock(self) -> WAVESExchangeClock:
        return self._clock

    def get_timestamp(self) -> int:
        """
        WavesEX time == time() * 1000
        DataDownloader time = time()
        """
        return self._clock.get_timestamp()

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
        timestamp = self._clock.get_waves_timestamp()
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
        price = self.get_orderbook()['bids'][0]['price']
        return price / 10 ** self._decimals[str(self.asset_pair_human_readable.price_asset)]

    def get_sell_price(self) -> float:
        price = self.get_orderbook()['asks'][0]['price']
        return price / 10 ** self._decimals[str(self.asset_pair_human_readable.price_asset)]

    def get_orderbook(self):  # type: ignore
        return self._request('get', f'orderbook/{str(self.asset_pair)}')

    def get_last_n_candles(self, n: int) -> tp.List[Candle]:
        self._fetch_candles()
        return self._candles[-n:]

    @retry(RuntimeError, tries=15, delay=3)
    def _request(self, request_type: str, api_request: str, body: str = '',
                 headers: tp.Optional[tp.Dict[str, tp.Any]] = None,
                 params: tp.Optional[tp.Dict[str, tp.Any]] = None) -> tp.Any:
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
        # https://docs.waves.exchange/en/waves-matcher/matcher-api
        scaled_price = int(price * 10 ** (8 + self._decimals[str(self.asset_pair_human_readable.price_asset)] -
                                          self._decimals[str(self.asset_pair_human_readable.amount_asset)]))
        scaled_amount = int(amount * 10 ** (self._decimals[str(self.asset_pair_human_readable.amount_asset)]))
        timestamp = self._clock.get_waves_timestamp()
        expiration = timestamp + self._max_lifetime * 1000
        optype: int = 0 if direction == Direction.BUY else 1
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
                                self._serialize_asset_id(self._fee_currency)
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
        print(response)
        if response['status'] != "OrderAccepted":
            # Sometimes order is created but response status is something else, so check current active orders
            self._fetch_orders()
            for order in self._active_orders:
                if order.timestamp == timestamp:
                    return order
            self.logger.warning(f"Order is not accepted. Status: {response['status']}")
            return None
        self._fetch_orders()

        # Order might be filled immediately if price == get_buy_price()
        if not any(map(lambda active_order: active_order.order_id == response['message']['id'], self._active_orders)) \
                and not any(map(lambda order_id: order_id == response['message']['id'], self._filled_order_ids)):
            return self._place_order(direction, amount, price)

        order = Order(order_id=response['message']['id'],
                      asset_pair=self.asset_pair_human_readable,
                      amount=amount,
                      price=price,
                      timestamp=timestamp,
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
        timestamp = self._clock.get_waves_timestamp()
        signature_data: bytes = b58decode(self._public_key) + \
                                pack(">Q", timestamp)
        signature: str = self._sign(signature_data)
        headers: tp.Dict[str, tp.Any] = {
            "accept": "application/json",
            "Timestamp": str(timestamp),
            "Signature": signature
        }
        url_params: tp.Dict[str, tp.Any] = {
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
                          price=int(params['price'] /
                                    (10 ** (8 + self._decimals[str(self.asset_pair_human_readable.price_asset)] -
                                            self._decimals[str(self.asset_pair_human_readable.amount_asset)]))),
                          amount=int(params['amount'] /
                                     (10 ** self._decimals[str(self.asset_pair_human_readable.amount_asset)])),
                          timestamp=params['timestamp'],
                          direction=Direction.from_string(params['type']))
            if (params['status'] == 'Accepted' or params['status'] == 'PartiallyFilled') and (fetch_all or active):
                self._active_orders.add(order)
            elif params['status'] == 'Cancelled' and (fetch_all or cancelled):
                self._cancelled_orders_ids.add(order.order_id)
            elif params['status'] == 'Filled' and (fetch_all or filled):
                self._active_orders.discard(order)
                self._filled_order_ids.add(order.order_id)

    def _fetch_candles(self) -> None:
        if self.get_timestamp() - self._clock.get_last_request() > self._clock.get_candles_update_rate():
            new_candles: tp.List[Candle] = MarketDataDownloader.get_candles(
                self.asset_pair_human_readable, self._candles_lifetime,
                TimeRange(self._clock.get_last_fetch(), self._clock.get_timestamp()))
            self._clock.update_last_request(self.get_timestamp())
            if new_candles:
                self._clock.update_last_fetch(new_candles[-1].ts)
                if self._candles and self._candles[-1].ts == new_candles[0].ts:
                    self._candles.pop()
                self._candles.extend(new_candles)

        # TODO: may be use collections.deque(max_len=const) for candles

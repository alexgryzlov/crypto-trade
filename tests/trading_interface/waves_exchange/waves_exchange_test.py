import pytest
import requests_mock
import json
import typing as tp
from trading import AssetPair, Asset

from trading_interface.waves_exchange.waves_exchange_interface import \
    WAVESExchangeInterface

from tests.logger.empty_logger_mock import empty_logger_mock
from helpers.typing.common_types import Config

from waves_exchange_responses import *

ti_config: Config = {
    "timeframe": "15m",
    "asset_pair": ["WAVES", "25FEqEjRkqK6yCkiT7Lz6SAYz7gUFCtxfCChnrVFD5AT"],
}
asset_pair = AssetPair(*[Asset(name) for name in ti_config["asset_pair"]])

exchange_config: Config = {
    "matcher": "https://matcher-testnet.waves.exchange",
    "matcher_fee": 300000,
    "price_shift": 100000000,
    "max_lifetime": 2592000,
    "version": 3,
    "private_key": "7WJxqTfaiMmFFHRvxCwiQ8DAE3qVBd5ziaE5F8qJWXWx",
    "public_key": "DuasNP39N7PCNCKfEkjXniR8otVbriYp3MpBrKKZrH1K"
}


def require_equal_structure(lhs: tp.Any,
                            rhs: tp.Any):
    assert isinstance(lhs, type(rhs)) or \
           isinstance(rhs, type(lhs))
    if isinstance(lhs, dict):  # not Mapping
        l_keys = sorted(lhs.keys())
        r_keys = sorted(rhs.keys())
        assert l_keys == r_keys
        for key in l_keys:
            require_equal_structure(lhs[key], rhs[key])
    elif isinstance(lhs, list) and \
            isinstance(rhs, list):  # not Sequence, str is Sequence
        for lhs_val in lhs:
            for rhs_val in rhs:
                require_equal_structure(lhs_val, rhs_val)


def make_request_url(api_request: str):
    return f"{exchange_config['matcher']}/matcher/{api_request}"


def setup_mocker(m: requests_mock.Mocker) -> requests_mock.Mocker:
    m.get(make_request_url(''),
          text=f'"{mock_matcher_pubkey}"')
    return m


def add_orderbook(m: requests_mock.Mocker,
                  orderbook=None) -> requests_mock.Mocker:
    if orderbook is None:
        orderbook = sample_orderbook
    m.get(make_request_url(f'orderbook/{str(asset_pair)}'),
          text=json.dumps(orderbook))
    return m


@requests_mock.Mocker(kw="m")
def test_init_matcher_public_key(empty_logger_mock: empty_logger_mock,
                                 **kwargs: requests_mock.Mocker):
    setup_mocker(kwargs["m"])
    ti = WAVESExchangeInterface(trading_config=ti_config,
                                exchange_config=exchange_config)
    assert ti.is_alive()
    # TODO: remove, don't access private members
    assert ti._matcher_public_key == mock_matcher_pubkey.encode('ascii')


def test_init_matcher_public_key_testnet(empty_logger_mock: empty_logger_mock):
    ti = WAVESExchangeInterface(trading_config=ti_config,
                                exchange_config=exchange_config)
    assert ti.is_alive()


@requests_mock.Mocker(kw="m")
def test_get_orderbook(empty_logger_mock: empty_logger_mock,
                       **kwargs: requests_mock.Mocker):
    m = setup_mocker(kwargs["m"])

    ti = WAVESExchangeInterface(trading_config=ti_config,
                                exchange_config=exchange_config)
    data = {"lol": 1}
    add_orderbook(m, data)

    assert ti.get_orderbook() == data


def test_get_orderbook_testnet(empty_logger_mock: empty_logger_mock):
    ti = WAVESExchangeInterface(trading_config=ti_config,
                                exchange_config=exchange_config)
    orderbook = ti.get_orderbook()

    timestamp = orderbook['timestamp']
    assert timestamp > 0

    resp_asset_pair = orderbook['pair']
    assert resp_asset_pair['amountAsset'] == asset_pair.amount_asset.name
    assert resp_asset_pair['priceAsset'] == asset_pair.price_asset.name

    assert isinstance(orderbook['bids'], list)
    assert isinstance(orderbook['asks'], list)


def test_orderbook_testnet_api_change(empty_logger_mock: empty_logger_mock):
    ti = WAVESExchangeInterface(trading_config=ti_config,
                                exchange_config=exchange_config)
    orderbook = ti.get_orderbook()
    require_equal_structure(orderbook, sample_orderbook)


@requests_mock.Mocker(kw="m")
def test_get_buy_price(empty_logger_mock: empty_logger_mock,
                       **kwargs: requests_mock.Mocker):
    m = setup_mocker(kwargs["m"])

    ti = WAVESExchangeInterface(trading_config=ti_config,
                                exchange_config=exchange_config)
    add_orderbook(m, sample_orderbook)

    buy_price = sample_orderbook['bids'][0]['price']
    resp_buy_price = ti.get_buy_price()
    assert buy_price == resp_buy_price


@requests_mock.Mocker(kw="m")
def test_get_sell_price(empty_logger_mock: empty_logger_mock,
                        **kwargs: requests_mock.Mocker):
    m = setup_mocker(kwargs["m"])

    ti = WAVESExchangeInterface(trading_config=ti_config,
                                exchange_config=exchange_config)
    add_orderbook(m, sample_orderbook)

    sell_price = sample_orderbook['asks'][0]['price']
    resp_sell_price = ti.get_sell_price()
    assert sell_price == resp_sell_price


@requests_mock.Mocker(kw="m")
def test_sell(empty_logger_mock: empty_logger_mock,
              **kwargs: requests_mock.Mocker):
    m = setup_mocker(kwargs["m"])
    ti = WAVESExchangeInterface(trading_config=ti_config,
                                exchange_config=exchange_config)
    add_orderbook(m, sample_orderbook)

    m.post(make_request_url('orderbook'),
           text=json.dumps(sample_sell_order_accepted))
    amount = sample_sell_order_accepted['message']['amount'] / 100000
    order = ti.sell(amount, ti.get_sell_price())
    assert order is not None


@requests_mock.Mocker(kw="m")
def test_sell_fail(empty_logger_mock: empty_logger_mock,
                   **kwargs: requests_mock.Mocker):
    m = setup_mocker(kwargs["m"])
    ti = WAVESExchangeInterface(trading_config=ti_config,
                                exchange_config=exchange_config)
    add_orderbook(m, sample_orderbook)

    m.post(make_request_url('orderbook'),
           text=json.dumps(sample_order_rejected))
    amount = sample_sell_order_accepted['message']['amount'] / 100000
    order = ti.sell(amount, ti.get_sell_price())
    assert order is None

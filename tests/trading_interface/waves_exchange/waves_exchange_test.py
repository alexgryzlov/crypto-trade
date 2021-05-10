import pytest
import requests_mock
import json

from trading_interface.waves_exchange.waves_exchange_interface import \
    WAVESExchangeInterface

from tests.logger.empty_logger_mock import empty_logger_mock
from helpers.typing.common_types import Config

ti_config: Config = {
    "timeframe": "15m",
    "asset_pair": ["WAVES", "25FEqEjRkqK6yCkiT7Lz6SAYz7gUFCtxfCChnrVFD5AT"],
}

exchange_config: Config = {
    "matcher": "https://matcher-testnet.waves.exchange",
    "matcher_fee": 300000,
    "price_shift": 100000000,
    "max_lifetime": 2592000,
    "version": 3,
    "private_key": "7WJxqTfaiMmFFHRvxCwiQ8DAE3qVBd5ziaE5F8qJWXWx",
    "public_key": "DuasNP39N7PCNCKfEkjXniR8otVbriYp3MpBrKKZrH1K"
}

mock_matcher_pubkey = "8QUAqtTckM5B8gvcuP7mMswat9SjKUuafJMusEoSn1Gy"


def make_request_url(api_request: str):
    return f"{exchange_config['matcher']}/matcher/{api_request}"


def setup_mocker(m: requests_mock.Mocker) -> requests_mock.Mocker:
    m.get(make_request_url(''),
          text=f'"{mock_matcher_pubkey}"')
    return m


@requests_mock.Mocker(kw="m")
def test_init_matcher_public_key(empty_logger_mock: empty_logger_mock,
                                 **kwargs: requests_mock.Mocker):
    setup_mocker(kwargs["m"])
    ti = WAVESExchangeInterface(trading_config=ti_config,
                                exchange_config=exchange_config)
    assert ti.is_alive()
    assert ti._matcher_public_key == mock_matcher_pubkey.encode('ascii')


def test_init_matcher_public_key_testnet(empty_logger_mock: empty_logger_mock):
    ti = WAVESExchangeInterface(trading_config=ti_config,
                                exchange_config=exchange_config)
    assert ti.is_alive()
    assert ti._matcher_public_key


@requests_mock.Mocker(kw="m")
def test_get_orderbook(empty_logger_mock: empty_logger_mock,
                       **kwargs: requests_mock.Mocker):
    m = setup_mocker(kwargs["m"])

    ti = WAVESExchangeInterface(trading_config=ti_config,
                                exchange_config=exchange_config)
    data = {"lol": 1}
    m.get(make_request_url(f'orderbook/{str(ti.asset_pair)}'),
          text=json.dumps(data))

    assert ti.get_orderbook() == data


def test_get_orderbook_testnet(empty_logger_mock: empty_logger_mock):
    ti = WAVESExchangeInterface(trading_config=ti_config,
                                exchange_config=exchange_config)
    orderbook = ti.get_orderbook()

    timestamp = orderbook['timestamp']
    assert timestamp > 0

    asset_pair = orderbook['pair']
    assert asset_pair['amountAsset'] == ti.asset_pair.amount_asset.name
    assert asset_pair['priceAsset'] == ti.asset_pair.price_asset.name

    assert isinstance(orderbook['bids'], list)
    assert isinstance(orderbook['asks'], list)

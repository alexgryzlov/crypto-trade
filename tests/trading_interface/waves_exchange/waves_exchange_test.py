import pytest
import requests_mock
import json
import typing as tp
from trading import AssetPair, Direction, Order

from trading_interface.waves_exchange.waves_exchange_interface import \
    WAVESExchangeInterface

from tests.logger.empty_logger_mock import empty_logger_mock, EmptyLoggerMock

from tests.configs.base_config import base_config, trading_interface_config
from tests.configs.exchange_config import exchange_config, testnet_config
from tests.trading_interface.waves_exchange.waves_exchange import *
from waves_exchange_samples import *


def require_equal_structure(lhs: tp.Any,
                            rhs: tp.Any) -> None:
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


def add_orderbook(
        m: requests_mock.Mocker,
        matcher_host: str,
        asset_pair: AssetPair,
        orderbook: tp.Optional[tp.Dict[str, tp.Any]] = None
) -> requests_mock.Mocker:
    if orderbook is None:
        orderbook = sample_orderbook
    url = make_request_url(f'orderbook/{str(asset_pair)}', matcher_host)
    m.get(make_request_url(f'orderbook/{str(asset_pair)}', matcher_host),
          text=json.dumps(orderbook))
    return m


def test_init_matcher_public_key(empty_logger_mock: EmptyLoggerMock,
                                 mock_matcher: requests_mock.Mocker,
                                 matcher_host: str,
                                 mock_exchange: WAVESExchangeInterface) -> None:
    assert mock_exchange.is_alive()
    # TODO: remove, don't access private members
    assert mock_exchange._matcher_public_key == \
           mock_matcher_pubkey.encode('ascii')


@pytest.mark.testnet
def test_init_matcher_public_key_testnet(
        empty_logger_mock: EmptyLoggerMock,
        real_exchange: WAVESExchangeInterface) -> None:
    assert real_exchange.is_alive()


def test_get_orderbook(empty_logger_mock: EmptyLoggerMock,
                       mock_matcher: requests_mock.Mocker,
                       mock_exchange: WAVESExchangeInterface,
                       matcher_host: str,
                       asset_addresses_pair: AssetPair) -> None:
    data = {"lol": 1}
    add_orderbook(mock_matcher, matcher_host, asset_addresses_pair, data)

    assert mock_exchange.get_orderbook() == data


@pytest.mark.testnet
def test_get_orderbook_testnet(empty_logger_mock: EmptyLoggerMock,
                               real_exchange: WAVESExchangeInterface,
                               asset_addresses_pair: AssetPair) -> None:
    orderbook = real_exchange.get_orderbook()

    timestamp = orderbook['timestamp']
    assert timestamp > 0

    resp_asset_pair = orderbook['pair']
    assert resp_asset_pair['amountAsset'] == asset_addresses_pair.amount_asset.name
    assert resp_asset_pair['priceAsset'] == asset_addresses_pair.price_asset.name

    assert isinstance(orderbook['bids'], list)
    assert isinstance(orderbook['asks'], list)


@pytest.mark.testnet
def test_orderbook_testnet_api_change(
        empty_logger_mock: EmptyLoggerMock,
        real_exchange: WAVESExchangeInterface) -> None:
    orderbook = real_exchange.get_orderbook()
    require_equal_structure(orderbook, sample_orderbook)


@pytest.mark.parametrize("direction,name_in_orderbook", [
    (Direction.SELL, 'asks'),
    (Direction.BUY, 'bids'),
])
def test_get_price(empty_logger_mock: EmptyLoggerMock,
                       mock_matcher: requests_mock.Mocker,
                       mock_exchange: WAVESExchangeInterface,
                       matcher_host: str,
                       asset_addresses_pair: AssetPair,
                       direction: Direction,
                       name_in_orderbook: str, ) -> None:
    add_orderbook(mock_matcher, matcher_host, asset_addresses_pair, sample_orderbook)

    price = sample_orderbook[name_in_orderbook][0]['price']  # type: ignore
    price /= sample_orderbook_price_scale
    if direction == Direction.SELL:
        resp_price = mock_exchange.get_sell_price()
    else:
        resp_price = mock_exchange.get_buy_price()
    assert resp_price == price


@pytest.mark.skip(reason="Interface checks if orderbook is updated => impossible to test")
@pytest.mark.parametrize("direction,response", [
    (Direction.SELL, sample_sell_order_accepted),
    (Direction.BUY, sample_buy_order_accepted),
    (Direction.SELL, sample_order_rejected),
    (Direction.BUY, sample_order_rejected)
])
def test_order_place(empty_logger_mock: EmptyLoggerMock,
                     mock_matcher: requests_mock.Mocker,
                     matcher_host: str,
                     mock_exchange: WAVESExchangeInterface,
                     asset_addresses_pair: AssetPair,
                     direction: str,
                     response: tp.Dict[str, tp.Any]) -> None:
    add_orderbook(mock_matcher, matcher_host, asset_addresses_pair, sample_orderbook)

    mock_matcher.post(make_request_url('orderbook', matcher_host),
                      text=json.dumps(response))
    amount = 1
    if direction == Direction.SELL:
        price = mock_exchange.get_sell_price()
        order = mock_exchange.sell(amount, price)
    else:
        price = mock_exchange.get_buy_price()
        order = mock_exchange.buy(amount, price)

    if response['success']:
        assert order is not None
    else:
        assert order is None

    order_request = mock_matcher.request_history[-1]
    request_body = json.loads(order_request.text)
    require_equal_structure(request_body, sample_place_order_request)

    assert request_body['matcherPublicKey'] == mock_matcher_pubkey
    assert request_body['assetPair']['amountAsset'] == \
           asset_addresses_pair.amount_asset.name
    assert request_body['assetPair']['priceAsset'] == \
           asset_addresses_pair.price_asset.name
    if direction == Direction.SELL:
        assert request_body['orderType'] == 'sell'
    else:
        assert request_body['orderType'] == 'buy'
    assert float(request_body['amount']) == amount * 10 ** 8
    assert float(request_body['price']) == price * sample_orderbook_price_scale


@pytest.mark.parametrize("response", [
    sample_order_canceled,
    sample_order_canceled_reject,
])
def test_cancel_order(empty_logger_mock: EmptyLoggerMock,
                      mock_matcher: requests_mock.Mocker,
                      matcher_host: str,
                      mock_exchange: WAVESExchangeInterface,
                      asset_addresses_pair: AssetPair,
                      response: tp.Dict[str, tp.Any]) -> None:
    add_orderbook(mock_matcher, matcher_host, asset_addresses_pair, sample_orderbook)

    mock_matcher.post(
        make_request_url(f'orderbook/{str(asset_addresses_pair)}/cancel', matcher_host),
        text=json.dumps(response))

    # only order_id needed
    order = Order(sample_order_id, asset_addresses_pair, 0, 0, 0, Direction.SELL)
    assert mock_exchange.cancel_order(order) == response['success']

    order_request = mock_matcher.request_history[-1]
    request_body = json.loads(order_request.text)
    require_equal_structure(request_body, sample_cancel_order_request)

    assert request_body['orderId'] == sample_order_id

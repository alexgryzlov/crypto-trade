import pytest
import requests_mock
import json
import typing as tp
from trading import AssetPair, Direction, Order

from trading_interface.waves_exchange.waves_exchange_interface import \
    WAVESExchangeInterface

from tests.logger.empty_logger_mock import empty_logger_mock, EmptyLoggerMock

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


def make_request_url(api_request: str,
                     matcher_host: str) -> str:
    return f"{matcher_host}/matcher/{api_request}"


def setup_mocker(m: requests_mock.Mocker,
                 matcher_host: str) -> requests_mock.Mocker:
    m.get(make_request_url('', matcher_host),
          text=f'"{mock_matcher_pubkey}"')
    return m


def add_orderbook(
        m: requests_mock.Mocker,
        matcher_host: str,
        asset_pair: AssetPair,
        orderbook: tp.Optional[tp.Dict[str, tp.Any]] = None
) -> requests_mock.Mocker:
    if orderbook is None:
        orderbook = sample_orderbook
    m.get(make_request_url(f'orderbook/{str(asset_pair)}', matcher_host),
          text=json.dumps(orderbook))
    return m


@requests_mock.Mocker(kw="m")
def test_init_matcher_public_key(empty_logger_mock: EmptyLoggerMock,
                                 matcher_host: str,
                                 exchange: WAVESExchangeInterface,
                                 **kwargs: requests_mock.Mocker) -> None:
    setup_mocker(kwargs["m"], matcher_host)
    assert exchange.is_alive()
    # TODO: remove, don't access private members
    assert exchange._matcher_public_key == mock_matcher_pubkey.encode('ascii')


def test_init_matcher_public_key_testnet(
        empty_logger_mock: EmptyLoggerMock,
        exchange: WAVESExchangeInterface) -> None:
    assert exchange.is_alive()


@requests_mock.Mocker(kw="m")
def test_get_orderbook(empty_logger_mock: EmptyLoggerMock,
                       exchange: WAVESExchangeInterface,
                       matcher_host: str,
                       asset_pair: AssetPair,
                       **kwargs: requests_mock.Mocker) -> None:
    m = setup_mocker(kwargs["m"], matcher_host)

    data = {"lol": 1}
    add_orderbook(m, matcher_host, asset_pair, data)

    assert exchange.get_orderbook() == data


def test_get_orderbook_testnet(empty_logger_mock: EmptyLoggerMock,
                               exchange: WAVESExchangeInterface,
                               asset_pair: AssetPair) -> None:
    orderbook = exchange.get_orderbook()

    timestamp = orderbook['timestamp']
    assert timestamp > 0

    resp_asset_pair = orderbook['pair']
    assert resp_asset_pair['amountAsset'] == asset_pair.amount_asset.name
    assert resp_asset_pair['priceAsset'] == asset_pair.price_asset.name

    assert isinstance(orderbook['bids'], list)
    assert isinstance(orderbook['asks'], list)


def test_orderbook_testnet_api_change(
        empty_logger_mock: EmptyLoggerMock,
        exchange: WAVESExchangeInterface) -> None:
    orderbook = exchange.get_orderbook()
    require_equal_structure(orderbook, sample_orderbook)


@pytest.mark.parametrize("direction,name_in_orderbook", [
    (Direction.SELL, 'asks'),
    (Direction.BUY, 'bids'),
])
@requests_mock.Mocker(kw="m")
def test_get_buy_price(empty_logger_mock: EmptyLoggerMock,
                       exchange: WAVESExchangeInterface,
                       matcher_host: str,
                       asset_pair: AssetPair,
                       price_shift: int,
                       direction: Direction,
                       name_in_orderbook: str,
                       **kwargs: requests_mock.Mocker) -> None:
    m = setup_mocker(kwargs["m"], matcher_host)

    add_orderbook(m, matcher_host, asset_pair, sample_orderbook)

    price = sample_orderbook[name_in_orderbook][0]['price']  # type: ignore
    if direction == Direction.SELL:
        resp_price = exchange.get_sell_price()
    else:
        resp_price = exchange.get_buy_price()
    assert price == resp_price


@pytest.mark.parametrize("direction,response", [
    (Direction.SELL, sample_sell_order_accepted),
    (Direction.BUY, sample_buy_order_accepted),
    (Direction.SELL, sample_order_rejected),
    (Direction.BUY, sample_order_rejected)
])
@requests_mock.Mocker(kw="m")
def test_order_place(empty_logger_mock: EmptyLoggerMock,
                     matcher_host: str,
                     exchange: WAVESExchangeInterface,
                     asset_pair: AssetPair,
                     price_shift: int,
                     direction: str,
                     response: tp.Dict[str, tp.Any],
                     **kwargs: requests_mock.Mocker) -> None:
    m = setup_mocker(kwargs["m"], matcher_host)
    add_orderbook(m, matcher_host, asset_pair, sample_orderbook)

    m.post(make_request_url('orderbook', matcher_host),
           text=json.dumps(response))
    amount = 1
    if direction == Direction.SELL:
        price = exchange.get_sell_price()
        order = exchange.sell(amount, price)
    else:
        price = exchange.get_buy_price()
        order = exchange.buy(amount, price)

    if response['success']:
        assert order is not None
    else:
        assert order is None

    order_request = m.request_history[-1]
    request_body = json.loads(order_request.text)
    require_equal_structure(request_body, sample_place_order_request)

    assert request_body['matcherPublicKey'] == mock_matcher_pubkey
    assert request_body['assetPair']['amountAsset'] == \
           asset_pair.amount_asset.name
    assert request_body['assetPair']['priceAsset'] == \
           asset_pair.price_asset.name
    if direction == Direction.SELL:
        assert request_body['orderType'] == 'sell'
    else:
        assert request_body['orderType'] == 'buy'
    assert float(request_body['amount']) == amount * price_shift
    assert float(request_body['price']) == price * price_shift


@pytest.mark.parametrize("response", [
    sample_order_canceled,
    sample_order_canceled_reject,
])
@requests_mock.Mocker(kw="m")
def test_cancel_order(empty_logger_mock: EmptyLoggerMock,
                      matcher_host: str,
                      exchange: WAVESExchangeInterface,
                      asset_pair: AssetPair,
                      response: tp.Dict[str, tp.Any],
                      **kwargs: requests_mock.Mocker) -> None:
    m = setup_mocker(kwargs["m"], matcher_host)
    add_orderbook(m, matcher_host, asset_pair, sample_orderbook)

    m.post(
        make_request_url(f'orderbook/{str(asset_pair)}/cancel', matcher_host),
        text=json.dumps(response))

    order = Order(sample_order_id, asset_pair, 0, 0, Direction.SELL)
    assert exchange.cancel_order(order) == response['success']

    order_request = m.request_history[-1]
    request_body = json.loads(order_request.text)
    require_equal_structure(request_body, sample_cancel_order_request)

    assert request_body['orderId'] == sample_order_id

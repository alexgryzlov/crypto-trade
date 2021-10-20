import pytest
import requests_mock
import typing as tp

from helpers.typing.common_types import Config

from trading import AssetPair
from trading_interface.waves_exchange.waves_exchange_interface import \
    WAVESExchangeInterface

from tests.configs.base_config import base_config, trading_interface_config
from tests.configs.exchange_config import exchange_config, testnet_config
from tests.trading_interface.waves_exchange.waves_exchange_samples import \
    mock_matcher_pubkey


@pytest.fixture
def asset_pair(trading_interface_config: Config) -> AssetPair:
    return AssetPair.from_string(*trading_interface_config["asset_pair"])


@pytest.fixture
def asset_addresses(testnet_config: Config) -> dict:
    return testnet_config['asset_addresses']


@pytest.fixture
def asset_addresses_pair(asset_addresses: dict, asset_pair: AssetPair) -> AssetPair:
    return AssetPair(
        *(asset_addresses[str(asset)] for asset in (asset_pair.amount_asset, asset_pair.price_asset))
    )


@pytest.fixture
def matcher_host(testnet_config: Config) -> str:
    return testnet_config['matcher']


def make_request_url(api_request: str,
                     matcher_host: str) -> str:
    return f"{matcher_host}/matcher/{api_request}"


@pytest.fixture
def mock_matcher(matcher_host: str) \
        -> tp.Generator[requests_mock.Mocker, None, None]:
    with requests_mock.Mocker() as m:
        m.get(make_request_url('', matcher_host),
              text=f'"{mock_matcher_pubkey}"')
        yield m


@pytest.fixture
def mock_exchange(mock_matcher: requests_mock.Mocker,
                  trading_interface_config: Config,
                  testnet_config: Config) -> WAVESExchangeInterface:
    return WAVESExchangeInterface(trading_config=trading_interface_config,
                                  exchange_config=testnet_config)


@pytest.fixture
def real_exchange(trading_interface_config: Config,
                  testnet_config: Config) -> WAVESExchangeInterface:
    return WAVESExchangeInterface(trading_config=trading_interface_config,
                                  exchange_config=testnet_config)

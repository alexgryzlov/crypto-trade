import pytest
import requests_mock

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
def price_shift(testnet_config: Config) -> int:
    return testnet_config['price_shift']


@pytest.fixture
def matcher_host(testnet_config: Config) -> str:
    return testnet_config['matcher']


def make_request_url(api_request: str,
                     matcher_host: str) -> str:
    return f"{matcher_host}/matcher/{api_request}"


def setup_mocker(m: requests_mock.Mocker,
                 matcher_host: str) -> requests_mock.Mocker:
    m.get(make_request_url('', matcher_host),
          text=f'"{mock_matcher_pubkey}"')
    return m


@pytest.fixture
def mock_matcher(matcher_host: str) -> requests_mock.Mocker:
    with requests_mock.Mocker() as m:
        yield setup_mocker(m, matcher_host)


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

import pytest
from helpers.typing.common_types import Config
from trading import AssetPair
from trading_interface.waves_exchange.waves_exchange_interface import \
    WAVESExchangeInterface
from tests.configs.base_config import base_config, trading_interface_config
from tests.configs.exchange_config import exchange_config, testnet_config


@pytest.fixture
def asset_pair(trading_interface_config: Config) -> AssetPair:
    return AssetPair.from_string(*trading_interface_config["asset_pair"])


@pytest.fixture
def price_shift(testnet_config: Config) -> int:
    return testnet_config['price_shift']


@pytest.fixture
def matcher_host(testnet_config: Config) -> str:
    return testnet_config['matcher']


@pytest.fixture
def exchange(trading_interface_config: Config,
             testnet_config: Config) -> WAVESExchangeInterface:
    return WAVESExchangeInterface(trading_config=trading_interface_config,
                                  exchange_config=testnet_config)

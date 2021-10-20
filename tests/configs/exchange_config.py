import pytest
from pathlib import Path

from helpers.typing.common_types import ConfigsScope, Config

from base.config_parser import ConfigParser


@pytest.fixture(scope="session")
def exchange_config() -> ConfigsScope:
    return ConfigParser.load_config(Path('configs/waves.json'))


@pytest.fixture(scope="session")
def testnet_config(exchange_config: ConfigsScope) -> Config:
    return exchange_config["testnet"]

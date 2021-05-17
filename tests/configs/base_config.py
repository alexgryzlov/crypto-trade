import pytest
from pathlib import Path

from helpers.typing.common_types import ConfigsScope, Config

from base.config_parser import ConfigParser


@pytest.fixture(scope="session")
def base_config() -> ConfigsScope:
    return ConfigParser.load_config(Path('tests/configs/base.json'))


@pytest.fixture(scope="session")
def simulator_config() -> Config:
    return ConfigParser.load_config(Path('tests/configs/simulator.json'))


@pytest.fixture(scope="session")
def trading_interface_config(base_config: ConfigsScope) -> Config:
    return base_config["trading_interface"]

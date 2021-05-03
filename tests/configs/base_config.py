import pytest
from pathlib import Path

from helpers.typing.common_types import ConfigsScope

from base.config_parser import ConfigParser


@pytest.fixture(scope="session")
def base_config() -> ConfigsScope:
    return ConfigParser.load_config(Path('tests/configs/base.json'))

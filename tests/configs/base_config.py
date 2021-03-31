import pytest
from pathlib import Path

from helpers.typing.common_types import ConfigsScope

from base.config_parser import ConfigParser


@pytest.fixture
def base_config() -> ConfigsScope:
    return ConfigParser.load_config(Path('configs/base.json'))

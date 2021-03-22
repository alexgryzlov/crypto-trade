import json
import typing as tp
from pathlib import Path

from helpers.typing.common_types import ConfigsScope


class ConfigParser:
    @classmethod
    def load_config(cls, config_path: Path) -> ConfigsScope:
        return json.load(config_path.open())

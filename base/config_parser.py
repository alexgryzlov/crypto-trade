import json
import typing as tp
from pathlib import Path

from helpers.typing.common_types import ConfigsScope


class ConfigParser:
    @staticmethod
    def load_config(config_path: Path) -> ConfigsScope:
        return json.load(config_path.open())

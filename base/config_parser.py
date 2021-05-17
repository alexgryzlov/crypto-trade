import json
import typing as tp
from pathlib import Path

from helpers.typing.common_types import Config, ConfigsScope


class ConfigParser:
    @staticmethod
    def load_config(config_path: Path) -> tp.Union[Config, ConfigsScope]:
        return json.load(config_path.open())

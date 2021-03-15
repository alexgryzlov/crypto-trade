import configparser
import typing as tp


class ConfigParser:
    def __init__(self):
        self.parser = configparser.ConfigParser()

    def load_config(self, config_path: str) -> tp.Dict[str, tp.Dict[str, tp.Any]]:
        self.parser.read(config_path)
        return {section: dict(self.parser[section]) for section in self.parser}

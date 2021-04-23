import logging
import pickle
from datetime import datetime
from pathlib import Path

from logger.clock import Clock
from logger.log_events import LogEvent

import typing as tp
from helpers.typing.common_types import Config

TRADING = logging.WARNING + 5
logging.addLevelName(TRADING, "TRADING")


class Logger:
    def __init__(self, name: str, config: Config = None):
        self.config = Logger._default_config if config is None else config
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        if self.config["file_output"]:
            self.logger.addHandler(self._get_trading_file_handler())
            self.logger.addHandler(self._get_info_file_handler())
        if self.config["std_output"]:
            self.logger.addHandler(self.__get_stream_handler())
        if not self.config["system_time"]:
            self.logger.addFilter(Logger.TimestampFilter())

    def __getattr__(self, item: str) -> tp.Any:
        return getattr(self.logger, item)

    @classmethod
    def set_default_config(cls, cfg: Config):
        cls._default_config = cfg

    @classmethod
    def set_clock(cls, clock: Clock) -> None:
        cls._clock = clock

    @classmethod
    def set_log_file_name(cls, name: str) -> None:
        cls._file_name = name

    @classmethod
    def set_logs_path(cls, path: Path) -> None:
        cls._logs_path = path

    @classmethod
    def get_logs_path(cls, logs_type: str) -> Path:
        return Path(cls._logs_path / logs_type)

    @classmethod
    def _get_file_handler(cls, filename: Path, level: int) -> logging.FileHandler:
        if filename not in cls._file_handlers:
            file_handler = logging.FileHandler(filename, mode='w')
            file_handler.setLevel(level)
            file_handler.setFormatter(logging.Formatter(*cls._log_format))
            cls._file_handlers[filename] = file_handler
        return cls._file_handlers[filename]

    @classmethod
    def _get_trading_file_handler(cls) -> logging.FileHandler:
        return cls._get_file_handler(
            cls.create_log_file('short', 'log'), TRADING)

    @classmethod
    def _get_info_file_handler(cls) -> logging.FileHandler:
        return cls._get_file_handler(
            cls.create_log_file('full', 'log'), logging.INFO)

    @staticmethod
    def __get_stream_handler() -> logging.StreamHandler:
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        stream_handler.setFormatter(logging.Formatter(*Logger._log_format))
        return stream_handler

    @classmethod
    def store_log(cls) -> None:
        with open(cls.create_log_file('dump', 'dump'), 'wb') as f:
            pickle.dump(cls._dump_logs, f)

    @staticmethod
    def create_log_file(log_type: str, ext: str) -> Path:
        filename = datetime.now().strftime('%d-%m-%Y_%H-%M-%S') if \
            Logger._file_name is None else Logger._file_name
        filename += f'_{log_type}.{ext}'
        path = Path(Logger._logs_path / log_type / filename)
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    def trading(self, log_event: LogEvent,
                *args: tp.Any, **kwargs: tp.Any) -> None:
        if self.isEnabledFor(TRADING):
            log_event.obj['ts'] = Logger._clock.get_timestamp()
            log_event.obj['event_type'] = log_event.__class__
            self._log(TRADING, log_event.msg, args, **kwargs)
            Logger._dump_logs.append(log_event.obj)

    class TimestampFilter(logging.Filter):
        """
        Using filter to change time inside every LogRecord
        https://docs.python.org/3/howto/logging-cookbook.html#filters-contextual
        """

        def filter(self, record: logging.LogRecord) -> bool:
            record.created = Logger._clock.get_timestamp()
            return True

    _clock = Clock()
    _log_format = ('[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s ',
                   '%m-%d %H:%M:%S')
    _file_handlers: tp.Dict[Path, logging.FileHandler] = {}
    _dump_logs: tp.List[LogEvent] = []
    _file_name: tp.Optional[str] = None
    _logs_path = Path('logs')
    _default_config: Config = None

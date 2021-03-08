import logging
from datetime import datetime
from pathlib import Path

from logger.clock import Clock
from logger.object_log import ObjectLog, PATH_TO_FULL_LOGS, \
    PATH_TO_SHORT_LOGS, PATH_TO_DUMPS


def _trading_handler(self, log_event, *args, **kws):
    if self.isEnabledFor(logging.TRADING):
        log_event.obj['ts'] = Logger._clock.get_timestamp()
        log_event.obj['event_type'] = log_event.__class__
        self._log(logging.TRADING, log_event.msg, args, **kws)
        self._object_log.add_event(log_event.obj)


logging.TRADING = logging.WARNING + 5
logging.addLevelName(logging.TRADING, "TRADING")
logging.Logger.trading = _trading_handler
logging.Logger._object_log = ObjectLog()


class Logger:
    def __init__(self, name, stdout=False):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(self.__get_trading_file_handler())
        self.logger.addHandler(self.__get_info_file_handler())
        self.logger.addFilter(Logger.TimestampFilter())
        if stdout:
            self.logger.addHandler(self.__get_stream_handler())

    def __getattr__(self, item):
        return getattr(self.logger, item)

    @staticmethod
    def set_clock(clock: Clock):
        Logger._clock = clock

    @staticmethod
    def set_log_file_name(name):
        Logger._file_name = name

    @staticmethod
    def __get_file_handler(filename: Path, level):
        if filename not in Logger._file_handlers:
            filename.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(filename, mode='w')
            file_handler.setLevel(level)
            file_handler.setFormatter(logging.Formatter(*Logger._log_format))
            Logger._file_handlers[filename] = file_handler
        return Logger._file_handlers[filename]

    @staticmethod
    def __get_trading_file_handler():
        filename = datetime.now().strftime('short-%d-%m-%Y_%H-%M-%S.log') if \
            Logger._file_name is None else Logger._file_name + '_short.log'
        return Logger.__get_file_handler(PATH_TO_SHORT_LOGS / filename,
            logging.TRADING)

    @staticmethod
    def __get_info_file_handler():
        filename = datetime.now().strftime('full-%d-%m-%Y_%H-%M-%S.log') if \
            Logger._file_name is None else Logger._file_name + '_full.log'
        return Logger.__get_file_handler(PATH_TO_FULL_LOGS / filename,
            logging.INFO)

    @staticmethod
    def __get_stream_handler():
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        stream_handler.setFormatter(logging.Formatter(*Logger._log_format))
        return stream_handler

    class TimestampFilter(logging.Filter):
        """
        Using filter to change time inside every LogRecord
        https://docs.python.org/3/howto/logging-cookbook.html#filters-contextual
        """
        def filter(self, record):
            record.created = Logger._clock.get_timestamp()
            return True

    _clock = Clock()
    _log_format = (f'[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s ',
                   '%m-%d %H:%M:%S')
    _file_handlers = {}
    _file_name = None

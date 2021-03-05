import logging

from logger.clock import Clock
from logger.object_log import ObjectLog


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
    def __get_trading_file_handler():
        file_handler = logging.FileHandler('short.log')
        file_handler.setLevel(logging.TRADING)
        file_handler.setFormatter(logging.Formatter(*Logger._log_format))
        return file_handler

    @staticmethod
    def __get_info_file_handler():
        file_handler = logging.FileHandler('full.log')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter(*Logger._log_format))
        return file_handler

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

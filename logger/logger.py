import logging

from logger.clock import Clock
from logger.object_log import ObjectLog

_log_format = (f'[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s ',
               '%m-%d %H:%M:%S')
_clock = None
logging.TRADING = logging.WARNING + 5


def __get_trading_file_handler():
    file_handler = logging.FileHandler('short.log')
    file_handler.setLevel(logging.TRADING)
    file_handler.setFormatter(logging.Formatter(*_log_format))
    return file_handler


def __get_info_file_handler():
    file_handler = logging.FileHandler('full.log')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(*_log_format))
    return file_handler


def __get_stream_handler():
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(logging.Formatter(*_log_format))
    return stream_handler


def __trading_handler(self, log_event, *args, **kws):
    if self.isEnabledFor(logging.TRADING):
        log_event.obj['ts'] = _clock.get_timestamp()
        log_event.obj['event_type'] = log_event.__class__
        self._log(logging.TRADING, log_event.msg, args, **kws)
        self._object_log.add_event(log_event.obj)


def set_clock(clock: Clock):
    global _clock
    _clock = clock


class TimestampFilter(logging.Filter):
    def filter(self, record):
        record.created = _clock.get_timestamp()
        return True


def get_logger(name):
    logging.addLevelName(logging.TRADING, "TRADING")
    logging.Logger.trading = __trading_handler
    logging.Logger._object_log = ObjectLog()

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(__get_trading_file_handler())
    logger.addHandler(__get_info_file_handler())
    logger.addFilter(TimestampFilter())
    # logger.addHandler(__get_stream_handler())
    return logger

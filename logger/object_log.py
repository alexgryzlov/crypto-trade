import pickle
from pathlib import Path
from datetime import datetime
from log_events import LogEvent
import typing as tp

PATH_TO_FULL_LOGS = Path('logs/full/')
PATH_TO_SHORT_LOGS = Path('logs/short/')
PATH_TO_DUMPS = Path('logs/dump/')


class Singleton(type):
    _instances: tp.Dict[type, tp.Any] = {}

    def __call__(cls, *args: tp.Any, **kwargs: tp.Any) -> tp.Any:
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args,
                                                                 **kwargs)
        return cls._instances[cls]


class ObjectLog(metaclass=Singleton):
    def __init__(self) -> None:
        self.log: tp.List[LogEvent] = []

    def add_event(self, event: LogEvent) -> None:
        self.log.append(event)

    def store_log(self) -> None:
        PATH_TO_DUMPS.mkdir(parents=True, exist_ok=True)
        filename = datetime.now().strftime('obj-log-%d-%m-%Y_%H-%M-%S.dump')
        with open(PATH_TO_DUMPS / filename, 'wb') as f:
            pickle.dump(self.log, f)

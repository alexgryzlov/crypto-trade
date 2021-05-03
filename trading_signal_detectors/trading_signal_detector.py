import typing as tp
from abc import ABC, abstractmethod

from trading import Signal


class TradingSignalDetector(ABC):
    @abstractmethod
    def get_trading_signals(self) -> tp.List[Signal]:
        pass

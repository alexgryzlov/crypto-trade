from trading import Signal
import typing as tp
from abc import ABC, abstractmethod


class TradingSignalDetector(ABC):
    @abstractmethod
    def get_trading_signals(self) -> tp.List[Signal]:
        pass

import typing as tp
from trading_system.trading_system_handler import TradingSystemHandler

TradingSystemHandlerT = tp.TypeVar('TradingSystemHandlerT',
                                   bound=TradingSystemHandler)

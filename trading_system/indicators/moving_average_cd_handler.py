import typing as tp

from trading_system.indicators.exp_moving_average_handler import \
    ExpMovingAverageHandler
from trading_system.trading_system_handler import TradingSystemHandler
from trading_interface.trading_interface import TradingInterface


class MovingAverageCDHandler(TradingSystemHandler):
    """ Moving Average Convergence/Divergence(MACD) """

    def __init__(self, trading_interface: TradingInterface, short: int = 12,
                 long: int = 26, average: int = 9):
        """
        MACD = EMA_s - EMA_l
        Signal = EMA_a(MACD)
        """
        super().__init__(trading_interface)
        self.ti = trading_interface

        self.short = short
        self.long = long
        self.average = average
        self.short_handler = ExpMovingAverageHandler(self.ti, self.short)
        self.long_handler = ExpMovingAverageHandler(self.ti, self.long)

        self.macd_values: tp.List[float] = []
        self.signal_values: tp.List[float] = []

    def get_name(self) -> str:
        return f'{type(self).__name__}_s{self.short}_l{self.long}'

    def get_required_handlers(self) -> tp.List[TradingSystemHandler]:
        return [self.short_handler, self.long_handler]

    def link_required_handlers(self, handlers: tp.List[TradingSystemHandler]) \
            -> None:
        self.short_handler = tp.cast(ExpMovingAverageHandler, handlers[0])
        self.long_handler = tp.cast(ExpMovingAverageHandler, handlers[1])

    def update(self) -> bool:
        if not super().received_new_candle():
            return False

        emas_short = self.short_handler.get_last_n_values(1)
        emas_long = self.long_handler.get_last_n_values(1)
        if len(emas_long) == 0 or len(emas_short) == 0:
            return False
        ema_short = emas_short[0]
        ema_long = emas_long[0]

        self.macd_values.append(ema_short - ema_long)
        self.signal_values.append(ExpMovingAverageHandler.calculate_from(
            self.macd_values[-self.average:]))
        return True

    def get_last_n_values(self, n: int) -> tp.List[tp.Tuple[float, float]]:
        """ Returns MACD and signal value. """
        return list(zip(self.macd_values[-n:], self.signal_values[-n:]))

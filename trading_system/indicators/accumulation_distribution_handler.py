from trading_system.trading_system_handler import TradingSystemHandler
from trading_interface.trading_interface import TradingInterface
from trading.candle import Candle

import typing as tp


class AccumulationDistributionHandler(TradingSystemHandler):
    """
        Accumulation/Distribution formula:

        AD[i] = AD[i-1] + CMFV[i], where
        CMFV[i] = volume[i]*((close[i] - low[i]) - (high[i] - close[i])) / (high[i] - low[i])

        param: start_candle: We start calculating AD from  (current_number_candle - start_candle) candle.
        In general, a rising A/D line helps confirm a rising price trend,
        while a falling A/D line helps confirm a price downtrend.
    """

    def __init__(self, trading_interface: TradingInterface, start_candle: int = 100) -> None:
        super().__init__(trading_interface)
        self.ti = trading_interface
        self.start_candle = start_candle
        self.values: tp.List[float] = []
        self.calculate_initial_values()

    def calculate_initial_values(self) -> None:
        candles = self.ti.get_last_n_candles(self.start_candle)
        self.values = self.calculate_from(candles)

    def update(self) -> None:
        if not super().received_new_candle():
            return

        candle = self.ti.get_last_n_candles(1)
        cmfv = self.calculate_from(candle)[0]

        self.values.append(cmfv + (self.values[-1] if self.values else 0))

    def get_last_n_values(self, n: int) -> tp.List[float]:
        return self.values[-n:]

    @staticmethod
    def calculate_from(candles: tp.List[Candle]) -> tp.List[float]:
        """
        Calculate AD for given list of candles.
        :param candles: list of candles.
        :return: list of AD[i]
        """
        ad_values: tp.List[float] = []
        for candle in candles:
            cmfv = candle.volume * ((candle.close - candle.low) - (candle.high - candle.close)) / (
                    candle.high - candle.low)
            ad_values.append(cmfv + (ad_values[-1] if ad_values else 0))
        return ad_values

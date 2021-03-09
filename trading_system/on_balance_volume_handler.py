from trading_system.trading_system_handler import TradingSystemHandler
from trading_interface.trading_interface import TradingInterface
from trading.candle import Candle

import typing as tp


class OnBalanceVolumeHandler(TradingSystemHandler):
    """
        On Balance Volume formula:

                            volume[i],  if close[i] > close[i-1]
        OBV[i] = OBV[i-1] +     0,      if close[i] == close[i-1]
                            -volume[i], if close[i] < close[i-1]

        param: start_candle: We start calculating OBV from  (current_number_candle - start_candle) candle.
        If the trend and this indicator have the same forward direction, it means that the trend is stable.
        If they have a different direction, it means that the trend is likely to change direction.
    """

    def __init__(self, trading_interface: TradingInterface, start_candle: int = 100) -> None:
        super().__init__(trading_interface)
        self.ti = trading_interface
        self.start_candle = start_candle
        self.values = []
        self.calculate_initial_values()

    def calculate_initial_values(self) -> None:
        candles = self.ti.get_last_n_candles(self.start_candle)
        self.values = self.calculate_from(candles)

    def update(self) -> None:
        if not super().received_new_candle():
            return

        candles = self.ti.get_last_n_candles(2)

        if len(candles) < 2:
            return

        self.values.append(self.values[-1] + self.calculate_from(candles)[-1])

    def get_last_n_values(self, n: int) -> tp.List[float]:
        return self.values[-n:]

    @staticmethod
    def calculate_from(candles: tp.List[Candle]) -> tp.List[float]:
        """
            Calculate OBV for given list of candles.
            :param candles: list of candles.
            :return: list of AD[i]
        """
        obv_values: tp.List[float] = [0]
        if not candles:
            return []
        for i in range(len(candles) - 1):
            if candles[i + 1].close > candles[i].close:
                obv_values.append(obv_values[-1] + candles[i + 1].volume)
            elif candles[i + 1].close == candles[i].close:
                obv_values.append(obv_values[-1])
            else:
                obv_values.append(obv_values[-1] - candles[i + 1].volume)
        return obv_values

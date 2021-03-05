from trading_system.trading_system_handler import TradingSystemHandler
from trading_interface.trading_interface import TradingInterface
from trading.candle import Candle


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
        if not len(candles):
            return

        prev_candle = candles[0]
        for candle in candles:
            if not self.values:
                self.values.append(0)
                continue
            self.calculate_next_value(candle, prev_candle)
            prev_candle = candle

    def calculate_next_value(self, new_candle: Candle, prev_candle: Candle) -> None:
        if new_candle.close > prev_candle.close:
            self.values.append(self.values[-1] + new_candle.volume)
        elif new_candle.close == prev_candle.close:
            self.values.append(self.values[-1])
        else:
            self.values.append(self.values[-1] - new_candle.volume)

    def update(self) -> None:
        if not super().received_new_candle():
            return

        candles = self.ti.get_last_n_candles(2)
        if len(candles) <= 1:
            return

        self.calculate_next_value(candles[-1], candles[-2])

    def get_last_n_values(self, n) -> list:
        return self.values[-n:]

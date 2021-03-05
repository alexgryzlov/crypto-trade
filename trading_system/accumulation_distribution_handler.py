from trading_system.trading_system_handler import TradingSystemHandler
from trading_interface.trading_interface import TradingInterface
from trading.candle import Candle


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
        self.values = []
        self.calculate_initial_values()

    def calculate_initial_values(self) -> None:
        candles = self.ti.get_last_n_candles(self.start_candle)
        if not len(candles):
            return

        for candle in candles:
            self.calculate_next_value(candle)

    def calculate_next_value(self, candle: Candle) -> None:
        cmfv = candle.volume * ((candle.close - candle.low) - (candle.high - candle.close)) / (candle.high - candle.low)
        self.values.append(cmfv + (self.values[-1] if self.values else 0))

    def update(self) -> None:
        if not super().received_new_candle():
            return

        candles = self.ti.get_last_n_candles(1)
        if not len(candles):
            return

        self.calculate_next_value(candles[0])

    def get_last_n_values(self, n) -> list:
        return self.values[-n:]

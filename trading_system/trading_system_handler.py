from trading_interface.trading_interface import TradingInterface


class TradingSystemHandler:
    def __init__(self, trading_interface: TradingInterface):
        self.ti = trading_interface
        self.last_candle_timestamp = -1

    def pre_add(self, handlers):
        """ For dependent handlers. """
        pass

    def get_name(self):
        """ Should be unique. """
        return type(self).__name__

    def received_new_candle(self):
        last_candle = self.ti.get_last_n_candles(1)
        if last_candle:
            last_candle = last_candle[0]
            if last_candle.ts != self.last_candle_timestamp:
                self.last_candle_timestamp = last_candle.ts
                return True
        return False

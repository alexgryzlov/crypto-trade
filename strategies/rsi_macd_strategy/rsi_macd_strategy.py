import trading_system.trading_system as ts
from strategies.strategy_base import StrategyBase

from logger.logger import Logger

from trading import TrendType
from trading_signal_detectors.relative_strength_index.relative_strength_index_signal import RsiSignal


class RSIMACDStrategy(StrategyBase):
    """
        RSI + MACD strategy
        buy when RSI signals oversold and MACD signals uptrend
        sell when RSI signals overbought and MACD signals downtrend
    """
    def __init__(self, asset_pair, **kwargs) -> None:
        self.asset_pair = asset_pair
        self.logger = Logger('RSIMACDStrategy')
        self.ts_threshold = kwargs['threshold']
        self.balance = kwargs['balance']
        self.ts = None
        self.last_macd_uptrend_ts = -1
        self.last_macd_downtrend_ts = -1
        self.last_rsi_oversold_ts = -1
        self.last_rsi_overbought_ts = -1

    def init_trading(self, trading_system: ts.TradingSystem) -> None:
        self.ts = trading_system

    def update(self) -> None:
        if self.balance > 0 and \
                self.last_macd_downtrend_ts >= self.last_macd_uptrend_ts and \
                self.last_rsi_overbought_ts >= self.last_rsi_oversold_ts and \
                min(self.last_macd_downtrend_ts, self.last_rsi_overbought_ts) > self.__get_timestamp_border():
            self.ts.sell(self.asset_pair, 1, self.ts.get_buy_price())
            self.balance -= 1
        elif self.balance < 1 and \
                self.last_macd_uptrend_ts >= self.last_macd_downtrend_ts and \
                self.last_rsi_oversold_ts >= self.last_rsi_overbought_ts and \
                min(self.last_macd_uptrend_ts, self.last_rsi_oversold_ts) > self.__get_timestamp_border():
            self.ts.buy(self.asset_pair, 1, self.ts.get_sell_price())
            self.balance += 1

    def handle_moving_average_cd_signal(self, trend) -> None:
        self.logger.info(f'Strategy received MACD signal of type {trend}')

        if trend == TrendType.UPTREND:
            self.last_macd_uptrend_ts = self.ts.get_timestamp()
        else:
            self.last_macd_downtrend_ts = self.ts.get_timestamp()

    def handle_relative_strength_index_signal(self, signal: RsiSignal) -> None:
        self.logger.info(f'Strategy received RSI signal of type {signal}')

        if signal == RsiSignal.OVERSOLD:
            self.last_rsi_oversold_ts = self.ts.get_timestamp()
        else:
            self.last_rsi_overbought_ts = self.ts.get_timestamp()

    def __get_timestamp_border(self):
        return self.ts.get_timestamp() - self.ts_threshold

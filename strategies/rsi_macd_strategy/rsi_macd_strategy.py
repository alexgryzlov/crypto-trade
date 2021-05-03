import trading_system.trading_system as ts
from strategies.strategy_base import StrategyBase

from logger.logger import Logger

from trading import TrendType, AssetPair
from trading_signal_detectors.relative_strength_index.relative_strength_index_signal import RSISignal, RSISignalType
from trading_system.indicators import RelativeStrengthIndexHandler, MovingAverageCDHandler


class RSIMACDStrategy(StrategyBase):
    """
        RSI + MACD strategy
        buy when RSI signals oversold and MACD signals uptrend
        sell when RSI signals overbought and MACD signals downtrend
    """

    def __init__(self, config) -> None:
        self.asset_pair = AssetPair(*config['asset_pair'])
        self.logger = Logger('RSIMACDStrategy')
        self.ts_threshold = config['threshold']
        self.ts = None
        self.last_macd_uptrend_ts = -1
        self.last_macd_downtrend_ts = -1
        self.last_rsi_oversold_ts = -1
        self.last_rsi_overbought_ts = -1
        self.last_rsi_value = -1.
        self.received_new_signal = False
        self.scale = config['amount_scale']
        self.offset = config['amount_offset']

    def init_trading(self, trading_system: ts.TradingSystem) -> None:
        self.ts = trading_system
        self.ts.add_handler(RelativeStrengthIndexHandler, params={"window_size": 9})
        self.ts.add_handler(MovingAverageCDHandler, params={})

    def update(self) -> None:
        if not self.received_new_signal:
            return

        if self.last_macd_downtrend_ts >= self.last_macd_uptrend_ts and \
                self.last_rsi_overbought_ts >= self.last_rsi_oversold_ts and \
                min(self.last_macd_downtrend_ts, self.last_rsi_overbought_ts) > self.__get_timestamp_border():
            self.ts.sell(self.asset_pair, self.scale * self.last_rsi_value + self.offset, self.ts.get_buy_price())

        elif self.last_macd_uptrend_ts >= self.last_macd_downtrend_ts and \
                self.last_rsi_oversold_ts >= self.last_rsi_overbought_ts and \
                min(self.last_macd_uptrend_ts, self.last_rsi_oversold_ts) > self.__get_timestamp_border():
            self.ts.buy(self.asset_pair, self.scale * self.last_rsi_value + self.offset, self.ts.get_sell_price())
        self.received_new_signal = False

    def handle_moving_average_cd_signal(self, trend) -> None:
        self.logger.info(f'Strategy received MACD signal of type {trend}')
        self.received_new_signal = True

        if trend == TrendType.UPTREND:
            self.last_macd_uptrend_ts = self.ts.get_timestamp()
        else:
            self.last_macd_downtrend_ts = self.ts.get_timestamp()

    def handle_relative_strength_index_signal(self, signal: RSISignal) -> None:
        self.logger.info(f'Strategy received RSI signal of type {signal.type}.')
        self.received_new_signal = True
        self.last_rsi_value = signal.value
        if signal.type == RSISignalType.OVERSOLD:
            self.last_rsi_oversold_ts = self.ts.get_timestamp()
        else:
            self.last_rsi_overbought_ts = self.ts.get_timestamp()

    def __get_timestamp_border(self) -> int:
        return self.ts.get_timestamp() - self.ts_threshold

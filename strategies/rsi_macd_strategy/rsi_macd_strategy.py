import trading_system.trading_system as ts
import typing as tp

from helpers.typing.common_types import Config
from strategies.strategy_base import StrategyBase

from logger.logger import Logger

from trading import TrendType, AssetPair, Signal
from trading_signal_detectors import TradingSignalDetector
from trading_signal_detectors.macd.macd_signal_detector import MACDSignalDetector
from trading_signal_detectors.relative_strength_index.relative_strength_index_signal import RSISignal, RSISignalType
from trading_signal_detectors.relative_strength_index.relative_strength_index_signal_detector import \
    RelativeStrengthIndexSignalDetector


class RSIMACDStrategy(StrategyBase):
    """
        RSI + MACD strategy
        buy when RSI signals oversold and MACD signals uptrend
        sell when RSI signals overbought and MACD signals downtrend
    """

    def __init__(self, config: Config) -> None:
        self.asset_pair = AssetPair(*config['asset_pair'])
        self.logger: Logger = Logger('RSIMACDStrategy')
        self.ts_threshold = config['threshold']
        self.ts: tp.Optional[ts.TradingSystem] = None
        self.last_macd_uptrend_ts: int = -1
        self.last_macd_downtrend_ts: int = -1
        self.last_rsi_oversold_ts: int = -1
        self.last_rsi_overbought_ts: int = -1
        self.last_rsi_value: float = -1.
        self.received_new_signal: bool = False
        self.scale: int = config['amount_scale']
        self.offset: int = config['amount_offset']

    def init_trading(self, trading_system: ts.TradingSystem) -> None:
        self.ts = trading_system

    def get_signal_detectors(self) -> tp.List[TradingSignalDetector]:
        return [
            MACDSignalDetector(self.ts),
            RelativeStrengthIndexSignalDetector(self.ts, 9),
        ]

    def update(self) -> None:
        if not self.received_new_signal:
            return

        if self.__sell():
            self.ts.sell(
                self.asset_pair,
                self.scale * self.last_rsi_value + self.offset,
                self.ts.get_buy_price(),
            )
        elif self.__buy():
            self.ts.buy(
                self.asset_pair,
                self.scale * self.last_rsi_value + self.offset,
                self.ts.get_sell_price(),
            )
        self.received_new_signal = False

    def handle_moving_average_cd_signal(self, trend: Signal) -> None:
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

    def __sell(self) -> bool:
        return self.last_macd_downtrend_ts >= self.last_macd_uptrend_ts and \
                self.last_rsi_overbought_ts >= self.last_rsi_oversold_ts and \
                min(self.last_macd_downtrend_ts, self.last_rsi_overbought_ts) > self.__get_timestamp_border()

    def __buy(self) -> bool:
        return self.last_macd_uptrend_ts >= self.last_macd_downtrend_ts and \
                self.last_rsi_oversold_ts >= self.last_rsi_overbought_ts and \
                min(self.last_macd_uptrend_ts, self.last_rsi_oversold_ts) > self.__get_timestamp_border()

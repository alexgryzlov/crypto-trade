import typing as tp

import trading_system.trading_system as ts
from logger.logger import Logger
from strategies.strategy_base import StrategyBase
from trading import AssetPair, TrendType


class EMASRSIStrategy(StrategyBase):
    def __init__(self, asset_pair: AssetPair, amount: float = 100.,
                 **kwargs: tp.Any) -> None:
        self.asset_pair = asset_pair
        self.logger = Logger('EMASRSIStrategy')
        self.amount = amount
        self.ts: tp.Optional[ts.TradingSystem] = None
        self.ema_trend: tp.Optional[TrendType] = None

    def init_trading(self, trading_system: ts.TradingSystem) -> None:
        self.ts = trading_system

    def update(self) -> None:
        pass

    def handle_exp_moving_average_signal(self, trend: TrendType) -> None:
        self.ema_trend = trend

    def handle_stochastic_rsi_signal(self, trend: TrendType) -> None:
        if (trend == TrendType.UPTREND and
                self.ema_trend == TrendType.UPTREND):
            self.ts.buy(  # type: ignore
                self.asset_pair,
                self.amount,
                self.ts.get_sell_price())  # type: ignore

        if (trend == TrendType.DOWNTREND and
                self.ema_trend == TrendType.DOWNTREND):
            self.ts.sell(  # type: ignore
                self.asset_pair,
                self.amount,
                self.ts.get_buy_price())  # type: ignore

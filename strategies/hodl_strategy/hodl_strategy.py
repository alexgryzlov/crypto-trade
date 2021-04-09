import trading_system.trading_system as ts
from strategies.strategy_base import StrategyBase

from logger.logger import Logger

from trading import AssetPair
import typing as tp

satoshi = 1e-8


class HodlStrategy(StrategyBase):
    def __init__(self, asset_pair: AssetPair) -> None:
        self.asset_pair = asset_pair
        self.logger = Logger('HodlStrategy')
        self.ts: tp.Optional[ts.TradingSystem] = None
        self.bought_all = False

    def init_trading(self, trading_system: ts.TradingSystem) -> None:
        self.ts = trading_system

    def update(self) -> None:
        assert self.ts is not None
        if not self.bought_all:
            amount = self.ts.wallet[self.ts.currency_asset] / self.ts.get_buy_price() - satoshi
            self.ts.buy(self.asset_pair, amount, self.ts.get_buy_price())
            self.bought_all = True

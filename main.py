from dateutil import parser

from strategy_runner.strategy_runner import StrategyRunner
from strategies.trend_strategy.trend_strategy import TrendStrategy

from trading import AssetPair, Asset, Timeframe

StrategyRunner().run_strategy(
    strategy=TrendStrategy,
    asset_pair=AssetPair(Asset('WAVES'), Asset('USDN')),
    timeframe=Timeframe('5m'),
    from_ts=int(parser.parse('2021-02-10 00:00:00').timestamp()),
    to_ts=int(parser.parse('2021-02-10 12:00:00').timestamp()))

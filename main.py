from strategy_runner.strategy_runner import StrategyRunner
from strategies.trend_strategy.trend_strategy import TrendStrategy
import pywaves as pw
from dateutil import parser

WAVES_USDN = pw.AssetPair(pw.WAVES,
                          pw.Asset('DG2xFkPdDwKUoBkzGAhQtLpSGzfXLiCYPEzeKH2Ad24p'))

StrategyRunner().run_strategy(
    strategy=TrendStrategy,
    asset_pair=WAVES_USDN,
    timeframe=5,
    from_ts=int(parser.parse('2021-02-10 00:00:00').timestamp()),
    to_ts=int(parser.parse('2021-02-10 12:00:00').timestamp()))

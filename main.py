from dateutil import parser

from strategy_runner.strategy_runner import StrategyRunner
from strategies.trend_strategy.trend_strategy import TrendStrategy

from trading.asset import AssetPair, Asset

# StrategyRunner().run_strategy(
#     strategy=TrendStrategy,
#     asset_pair=AssetPair(Asset('WAVES'), Asset('USDN')),
#     timeframe=5,
#     from_ts=int(parser.parse('2021-02-10 00:00:00').timestamp()),
#     to_ts=int(parser.parse('2021-02-10 12:00:00').timestamp()))

from market_data_api.market_data_downloader import MarketDataDownloader

print(len(MarketDataDownloader().get_candles(
    AssetPair(Asset('WAVES'), Asset('USDN')),
    5,
    from_ts=int(parser.parse('2021-02-2 00:00:00').timestamp()),
    to_ts=int(parser.parse('2021-03-01 12:00:00').timestamp()))))

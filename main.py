from strategy_runner.strategy_runner import StrategyRunner
from strategies.trend_strategy.trend_strategy import TrendStrategy

from trading import AssetPair, Asset, Timeframe, TimeRange

StrategyRunner().do_strategy_multiple_run(
    strategy=TrendStrategy,
    asset_pair=AssetPair(Asset('WAVES'), Asset('USDN')),
    timeframe=Timeframe('5m'),
    time_range=TimeRange.from_iso_format(
        from_ts='2021-02-10 00:00:00',
        to_ts='2021-02-12 00:00:00'),
    runs=4,
    processes=2)

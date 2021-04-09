from copy import copy
from pathlib import Path

from market_data_api.market_data_downloader import MarketDataDownloader
from base.config_parser import ConfigParser
from strategies.rsi_macd_strategy.rsi_macd_strategy import RSIMACDStrategy

from strategy_runner.strategy_runner import StrategyRunner
from strategies.trend_strategy.trend_strategy import TrendStrategy

from trading import TimeRange, Timeframe, AssetPair, Asset

if __name__ == "__main__":
    base_config = ConfigParser.load_config(Path('configs/base.json'))

    MarketDataDownloader.init(copy(base_config['market_data_downloader']))

    strategy_runner = StrategyRunner(
        base_config=base_config)

    strategy_runner.run_strategy(
        strategy=RSIMACDStrategy,
        strategy_config={
            'threshold': Timeframe('3h').to_seconds(),
            'amount_scale': 7,
            'amount_offset': 3,
            'asset_pair': AssetPair(Asset('USDN'), Asset('WAVES')),
        },
        time_range=TimeRange.from_iso_format(
            from_ts='2021-02-01 00:00:00',
            to_ts='2021-03-01 12:00:00'),
    )

from pathlib import Path

from market_data_api.market_data_downloader import MarketDataDownloader
from base.config_parser import ConfigParser

from strategy_runner.strategy_runner import StrategyRunner
from strategies.trend_strategy.trend_strategy import TrendStrategy

from trading import TimeRange

from trading_interface.waves_exchange.waves_exchange_interface import WAVESExchangeInterface

if __name__ == "__main__":
    base_config = ConfigParser.load_config(Path('configs/mainnet_test.json'))

    MarketDataDownloader.init(base_config['market_data_downloader'])

    strategy_runner = StrategyRunner(
        base_config=base_config,
        simulator_config=ConfigParser.load_config(Path('configs/simulator.json')),
        exchange_config=ConfigParser.load_config(Path('configs/waves.json')))

    strategy_runner.run_exchange(
        strategy=TrendStrategy,
        strategy_config={}
    )

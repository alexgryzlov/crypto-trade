from pathlib import Path

from logger.logger import Logger
from market_data_api.market_data_downloader import MarketDataDownloader
from base.config_parser import ConfigParser

from strategies.strategy_runner import StrategyRunner

from trading import TimeRange


# It fails on testnet, because orderbook is empty
if __name__ == '__main__':
    base_config = ConfigParser.load_config(Path('configs/base.json'))
    waves_config = ConfigParser.load_config(Path('configs/waves.json'))['testnet']
    simulator_config = ConfigParser.load_config(Path('configs/simulator.json'))
    Logger.set_default_config(base_config['default_logger'])

    MarketDataDownloader.init(base_config['market_data_downloader'])

    strategy_runner = StrategyRunner(
        base_config=base_config,
        simulator_config=simulator_config,
        exchange_config=waves_config
    )

    # strategy_runner.run_exchange()

    strategy_runner.run_simulation(
        time_range=TimeRange.from_iso_format(
            from_ts='2020-09-01 00:00:00',
            to_ts='2020-11-01 12:00:00')
    )
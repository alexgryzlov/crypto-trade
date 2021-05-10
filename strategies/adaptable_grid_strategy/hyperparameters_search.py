import json
import typing as tp
from itertools import product
from pathlib import Path

from numpy import prod
from rich.console import Console

from base.config_parser import ConfigParser
from market_data_api.market_data_downloader import MarketDataDownloader
from strategy_runner.strategy_runner import StrategyRunner
from trading import TimeRange
from trading_system.trading_statistics import TradingStatistics


def generate_config(config: tp.Dict[str, tp.Any]) -> None:
    with open('strategies/adaptable_grid_strategy/config.json', 'w') as f:
        json.dump(config, f)


def grid_generator(
        grids: tp.List[tp.Dict[str, tp.List[tp.Any]]]
        ) -> tp.Generator[tp.Dict[str, tp.Any], None, None]:
    names = list(grids[0].keys())
    param_grid: tp.List[tp.Any] = sum(
        [list(product(*list(grid.values()))) for grid in grids], [])
    for params in param_grid:
        yield dict(zip(names, params))


time_range = TimeRange.from_iso_format(
    from_ts='2021-01-01 00:00:00',
    to_ts='2021-05-01 00:00:00')
base_config = ConfigParser.load_config(Path('configs/base.json'))
MarketDataDownloader.init(base_config['market_data_downloader'])
strategy_runner = StrategyRunner(base_config=base_config)
console = Console()

fee = 0.1
window_grid = [25, 30, 35]
coef_grid = [16, 17, 18]
timeout_grid = [16, 18, 20]
total_levels_grid = [9, 11, 13, 15]
param_grids: tp.List[tp.Dict[str, tp.List[tp.Any]]] = [{
  'asset_pair': [['USDT', 'USDN']],
  'total_levels': total_levels_grid,
  'threshold': [0.],
  'window': window_grid,
  'coef': coef_grid,
  'candles_timeout': timeout_grid,
  'candles_lifetime': [8],
  'timeout_only': [True],
  'handle_filled_orders': [True, False]
}]
total = sum(prod(list(
    map(len, param_grid.values()))) for param_grid in param_grids)
best_profit = float('-inf')
best_stats: tp.Optional[TradingStatistics] = None
best_params: tp.Dict[str, tp.List[tp.Any]] = {}

for i, params_dict in enumerate(grid_generator(param_grids)):
    generate_config(params_dict)
    stats = strategy_runner.run_strategy(time_range=time_range)
    profit = stats.calc_absolute_delta() - fee * stats.filled_order_count
    console.print(f'Checked {i + 1} out of {total}')
    if profit > best_profit:
        best_profit = profit
        best_stats = stats
        best_params = params_dict

color = 'green' if best_profit > 0 else 'red'
console.print('[bold]Optimal parameters:[/bold]')
console.print(best_params)
console.print(
    f'[bold]Profit (including fee): [{color}]{best_profit:.1f}[/{color}] '
    f'{best_stats.price_asset}[/bold]')

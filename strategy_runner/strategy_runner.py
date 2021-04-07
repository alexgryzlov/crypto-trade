import multiprocessing as mp
import traceback as tb
import typing as tp
from pathlib import Path

from helpers.typing.common_types import Config, ConfigsScope

from trading_interface.simulator.simulator import Simulator
from trading_signal_detectors.macd.macd_signal_detector import MACDSignalDetector
from trading_signal_detectors.relative_strength_index.relative_strength_index_signal_detector import \
    RelativeStrengthIndexSignalDetector

from trading_system.trading_system import TradingSystem
from trading_system.trading_statistics import TradingStatistics

from trading_signal_detectors.extremum.extremum_signal_detector \
    import ExtremumSignalDetector
from trading_signal_detectors.moving_average.moving_average_signal_detector \
    import MovingAverageSignalDetector

from strategies.strategy_base import StrategyBase

from logger.logger import Logger

from trading import Timestamp, TimeRange


class StrategyRunner:
    def __init__(self, base_config: ConfigsScope):
        self.base_config = base_config

    def run_strategy(
            self,
            strategy: tp.Type[StrategyBase],
            strategy_config: Config,
            time_range: TimeRange,
            logs_path: tp.Optional[Path] = None) -> TradingStatistics:

        Logger.set_log_file_name(Timestamp.to_iso_format(time_range.from_ts))
        if logs_path is not None:
            Logger.set_logs_path(logs_path)

        simulator = Simulator(
            time_range=time_range,
            config=self.base_config['trading_interface'])
        Logger.set_clock(simulator.get_clock())

        trading_system = TradingSystem(
            trading_interface=simulator,
            config=self.base_config['trading_system'])

        signal_detectors = [
            trading_system,
            ExtremumSignalDetector(trading_system, 2),
            MovingAverageSignalDetector(trading_system, 25, 50),
            RelativeStrengthIndexSignalDetector(trading_system, 9),
            MACDSignalDetector(trading_system),
        ]

        strategy_inst = strategy(**strategy_config)
        strategy_inst.init_trading(trading_system)

        while simulator.is_alive():
            trading_system.update()
            signals = []
            for detector in signal_detectors:
                signals += detector.get_trading_signals()
            for signal in signals:
                strategy_inst.__getattribute__(
                    f'handle_{signal.name}_signal')(signal.content)
            strategy_inst.update()

        trading_system.stop_trading()
        simulator.stop_trading()
        trading_system.update()

        stats = trading_system.get_trading_statistics()
        Logger.store_log()
        print(stats)

        return stats

    def run_strategy_on_periods(
            self,
            strategy: tp.Type[StrategyBase],
            strategy_config: Config,
            time_range: TimeRange,
            period: tp.Optional[int] = None,
            runs: tp.Optional[int] = None,
            visualize: bool = False,
            processes: int = 4,
            logs_path: tp.Optional[Path] = None) -> TradingStatistics:

        if period is None and runs is None:
            raise ValueError('Run type not selected')

        period = period if period is not None else \
            time_range.get_range() // runs  # type: ignore
        runs = runs if runs is not None else \
            time_range.get_range() // period

        pool = mp.Pool(processes=processes, maxtasksperchild=1)
        current_ts = time_range.from_ts
        run_results: tp.List[TradingStatistics] = []

        for run_id in range(runs):
            next_ts = current_ts + period
            pool.apply_async(
                self.run_strategy,
                kwds={
                    'strategy': strategy,
                    'strategy_config': strategy_config,
                    'time_range': TimeRange(current_ts, next_ts),
                    'logs_path': logs_path},
                callback=lambda run_result: run_results.append(run_result),
                error_callback=lambda e: tb.print_exception(type(e), e, None))
            current_ts = next_ts

        pool.close()
        pool.join()
        stats = TradingStatistics.merge(run_results)
        print(stats)

        if visualize:
            TradingStatistics.visualize(run_results)

        return stats

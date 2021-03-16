import multiprocessing as mp
import plotly.graph_objects as go
import typing as tp

from trading_interface.simulator.clock_simulator import ClockSimulator
from trading_interface.simulator.simulator import Simulator
from trading_system.trading_system import TradingSystem

from trading_signal_detectors.extremum.extremum_signal_detector \
    import ExtremumSignalDetector
from trading_signal_detectors.moving_average.moving_average_signal_detector \
    import MovingAverageSignalDetector

from logger.object_log import ObjectLog
from logger.logger import Logger

from trading import AssetPair, Timestamp, Timeframe, TimeRange


class RunResult:
    def __init__(self, time_range: TimeRange, balance: float):
        self.time_range = time_range
        self.balance = balance

    @staticmethod
    def get_balance_from(run_results: tp.List['RunResult']) -> tp.List[float]:
        return [r.balance for r in run_results]

    @staticmethod
    def get_timestamp_from(run_results: tp.List['RunResult']) -> tp.List[str]:
        return [Timestamp.to_iso_format(r.time_range.from_ts) for r in run_results]


class StrategyRunner:
    def __init__(self, base_config: tp.Dict[str, tp.Dict[str, tp.Any]]):
        self.base_config = base_config

    def run_strategy(
            self,
            strategy,
            strategy_config: tp.Dict[str, tp.Any],
            asset_pair: AssetPair,
            timeframe: Timeframe,
            time_range: TimeRange) -> RunResult:

        clock = ClockSimulator(
            start_ts=time_range.from_ts,
            timeframe=timeframe,
            config=self.base_config['clock_simulator'])

        trading_interface = Simulator(
            asset_pair=asset_pair,
            time_range=time_range,
            config=self.base_config['simulator'],
            clock=clock)

        Logger.set_clock(clock)
        Logger.set_log_file_name(time_range.to_iso_format())

        trading_system = TradingSystem(
            trading_interface=trading_interface,
            config=self.base_config['trading_system'])

        signal_detectors = [
            ExtremumSignalDetector(trading_system, 2),
            MovingAverageSignalDetector(trading_system, 25, 50)]

        strategy = strategy(trading_system=trading_system,
                            asset_pair=asset_pair,
                            **strategy_config)

        while trading_interface.is_alive():
            trading_system.update()
            signals = []
            for detector in signal_detectors:
                signals += detector.get_trading_signals()
            for signal in signals:
                strategy.__getattribute__(
                    f'handle_{signal.name}_signal')(signal.content)
            strategy.update()

        trading_system.stop_trading()

        print(time_range.to_iso_format())
        print(str(trading_system.get_trading_statistics()))

        ObjectLog().store_log()

        return RunResult(time_range, trading_system.get_balance())

    def run_strategy_on_periods(
            self,
            strategy,
            strategy_config: tp.Dict[str, tp.Any],
            asset_pair: AssetPair,
            timeframe: Timeframe,
            time_range: TimeRange,
            period: tp.Optional[int] = None,
            runs: tp.Optional[int] = None,
            visualize: bool = False,
            processes: int = 4):

        if period is None and runs is None:
            raise ValueError('Run type not selected')

        period = period if period is not None else \
            time_range.get_range() // runs
        runs = runs if runs is not None else \
            time_range.get_range() // period

        pool = mp.Pool(processes=processes, maxtasksperchild=1)
        current_ts = time_range.from_ts
        run_results = []

        for run_id in range(runs):
            next_ts = current_ts + period
            pool.apply_async(
                self.run_strategy,
                kwds={
                    'strategy': strategy,
                    'strategy_config': strategy_config,
                    'asset_pair': asset_pair,
                    'timeframe': timeframe,
                    'time_range': TimeRange(current_ts, next_ts)},
                callback=lambda run_result: run_results.append(run_result))
            current_ts = next_ts

        pool.close()
        pool.join()
        run_results.sort(key=lambda r: r.time_range.from_ts)

        if visualize:
            self.visualize_run_results(run_results)

    @staticmethod
    def visualize_run_results(run_results: tp.List[RunResult]):
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=RunResult.get_timestamp_from(run_results),
            y=RunResult.get_balance_from(run_results),
            marker_color=['green' if balance > 0 else 'red'
                          for balance in RunResult.get_balance_from(run_results)]))
        fig.show()

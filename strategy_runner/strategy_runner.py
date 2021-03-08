import multiprocessing as mp
import typing as tp

from trading_interface.simulator.clock_simulator import ClockSimulator
from trading_interface.simulator.simulator import Simulator
from trading_system.trading_system import TradingSystem

from trading_signal_detectors.extremum.extremum_signal_detector import ExtremumSignalDetector
from trading_signal_detectors.moving_average.moving_average_signal_detector import MovingAverageSignalDetector

from logger.object_log import ObjectLog
from logger.logger import Logger

from trading import AssetPair, Timeframe, TimeRange


class StrategyRunner:
    def __init__(self):
        pass

    def run_strategy(
            self,
            strategy,
            asset_pair: AssetPair,
            timeframe: Timeframe,
            time_range: TimeRange,
            candles_lifetime: int = 20):
        clock = ClockSimulator(
            start_ts=time_range.from_ts,
            timeframe=timeframe,
            candles_lifetime=candles_lifetime)

        trading_interface = Simulator(
            asset_pair=asset_pair,
            time_range=time_range,
            clock=clock)

        Logger.set_clock(clock)
        Logger.set_log_file_name(time_range.to_iso_format())

        trading_system = TradingSystem(trading_interface)

        signal_detectors = [
            ExtremumSignalDetector(trading_system, 2),
            MovingAverageSignalDetector(trading_system, 25, 50)]

        strategy = strategy(
            trading_system=trading_system,
            asset_pair=asset_pair)

        while trading_interface.is_alive():
            trading_system.update()
            signals = []
            for detector in signal_detectors:
                signals += detector.get_trading_signals()
            for signal in signals:
                strategy.__getattribute__(f'handle_{signal.name}_signal')(signal.content)
            strategy.update()

        print(time_range.to_iso_format())
        print(trading_system.get_balance())
        print(trading_system.get_active_orders())
        print(trading_system.get_wallet(), end='\n\n')

        ObjectLog().store_log()

    def do_strategy_multiple_run(
            self,
            strategy,
            asset_pair: AssetPair,
            timeframe: Timeframe,
            time_range: TimeRange,
            candles_lifetime: int = 20,
            one_run_duration: tp.Optional[int] = None,
            runs: tp.Optional[int] = None,
            processes: int = 4):
        if one_run_duration is None and runs is None:
            raise ValueError('Run type not selected')

        one_run_duration = one_run_duration if one_run_duration is not None else \
            time_range.get_range() // runs
        runs = runs if runs is not None else \
            time_range.get_range() // one_run_duration

        pool = mp.Pool(processes=processes, maxtasksperchild=1)
        current_ts = time_range.from_ts

        for run_id in range(runs):
            next_ts = current_ts + one_run_duration
            pool.apply_async(self.run_strategy, kwds={
                'strategy': strategy,
                'asset_pair': asset_pair,
                'timeframe': timeframe,
                'time_range': TimeRange(current_ts, next_ts),
                'candles_lifetime': candles_lifetime
            })
            current_ts = next_ts

        pool.close()
        pool.join()

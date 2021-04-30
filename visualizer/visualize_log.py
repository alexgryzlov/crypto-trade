import sys

sys.path.append('.')

import os
import pickle
import typing as tp
from pathlib import Path
from collections import defaultdict

import logger.log_events as log_events
from logger.logger import Logger
from visualizer.visualizer import Visualizer
from trading import Candle

LogEntryType = tp.Dict[str, tp.Any]
DecomposedLogType = tp.Dict[tp.Type[log_events.LogEvent],
                            tp.List[LogEntryType]]


def get_log_path() -> tp.Optional[Path]:
    path = Path(
        sys.argv[1] if len(sys.argv) == 2 else Logger.get_logs_path('dump'))
    logs = list(path.rglob('*.dump')) if path.is_dir() else [path]
    if not logs:
        return None
    return max(logs, key=os.path.getctime)


def load_log(filename: Path) -> tp.List[tp.Dict[str, tp.Any]]:
    with open(filename, 'rb') as f:
        log = pickle.load(f)
    return log


def decompose_log(log: tp.List[LogEntryType]) \
        -> DecomposedLogType:
    events = defaultdict(list)
    for event in log:
        events[event['event_type']].append(event)
    return events


def get_candles(candles_log: tp.List[LogEntryType]) \
        -> tp.List[Candle]:
    return [candle['candle'] for candle in candles_log]


def process_buy_sell_events(events: tp.List[LogEntryType]) \
        -> tp.Tuple[
            tp.List[int], tp.List[float], tp.List[float], tp.List[str]]:
    timestamps = [event['ts'] for event in events]
    amounts = [event['amount'] for event in events]
    prices = [event['price'] for event in events]
    meta: tp.List[str] = [''] * len(events)
    for i, item in enumerate(events):
        item.pop('event_type')
        meta[i] = '<br>'.join(
            str(key) + ': ' + str(value) for key, value in item.items())
    return timestamps, prices, amounts, meta


def extract_curve_events(
        decomposed_log: DecomposedLogType
) -> tp.List[tp.Type[log_events.CurveEvent]]:
    curve_events: tp.List[tp.Type[log_events.CurveEvent]] = []
    for event_type in decomposed_log:
        if issubclass(event_type, log_events.CurveEvent):
            curve_events.append(event_type)
    return curve_events


def decompose_by_params(all_curve_events: tp.List[LogEntryType]) \
        -> tp.Dict[str, tp.List[LogEntryType]]:
    curve_by_params = defaultdict(list)
    for event in all_curve_events:
        curve_by_params[event['params']].append(event)
    return curve_by_params


def get_all_curve_names(decomposed_log: DecomposedLogType) -> tp.List[str]:
    all_names = set()
    for curve_type in extract_curve_events(decomposed_log):
        for param, events in \
                decompose_by_params(decomposed_log[curve_type]).items():
            curve_name = ' '.join([curve_type.name, param])
            all_names.add(curve_name)
    return list(all_names)


def create_visualizer_from_log(
        decomposed_log: DecomposedLogType) -> Visualizer:
    vis = Visualizer()
    vis.add_candles(get_candles(decomposed_log[log_events.NewCandleEvent]))
    vis.add_trend_lines(decomposed_log[log_events.TrendLinesEvent])

    for curve_type in extract_curve_events(decomposed_log):
        for param, events in \
                decompose_by_params(decomposed_log[curve_type]).items():
            curve_name = ' '.join([curve_type.name, param])
            vis.add_curve(events, curve_name)

    vis.add_buy_events(
        *process_buy_sell_events(decomposed_log[log_events.BuyEvent]))
    vis.add_sell_events(
        *process_buy_sell_events(decomposed_log[log_events.SellEvent]))
    return vis


if __name__ == '__main__':
    path = get_log_path()
    if path is None:
        print('Log not found')
        exit(0)
    print(path)
    log = load_log(path)
    decomposed_log = decompose_log(log)
    vis = create_visualizer_from_log(decomposed_log)
    fig = vis.plot()
    fig.show()

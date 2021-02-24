import sys

sys.path.append('.')

import pickle
import logger.log_events as log_events
import typing as tp
from collections import defaultdict
from visualizer import Visualizer


def load_log(filename='object_log.dump'):
    with open(filename, 'rb') as f:
        log = pickle.load(f)
    return log


def decompose_log(log: tp.List[tp.Mapping[str, tp.Any]]):
    events = defaultdict(list)
    for event in log:
        events[event['event_type']].append(event)
    return events


def get_candles(candles_log):
    return [candle['candle'] for candle in candles_log]


def process_buy_sell_events(events):
    timestamps = [event['ts'] for event in events]
    amounts = [event['amount'] for event in events]
    prices = [event['price'] for event in events]
    meta = events.copy()
    for i, item in enumerate(meta):
        item.pop('event_type')
        meta[i] = '<br>'.join(str(key) + ': ' + str(value) for key, value in item.items())
    return timestamps, prices, amounts, meta


if __name__ == '__main__':
    log = load_log()
    decomposed_log = decompose_log(log)
    vis = Visualizer()
    vis.add_candles(get_candles(decomposed_log[log_events.NewCandleEvent]))
    vis.add_trend_lines(decomposed_log[log_events.TrendLinesEvent])
    vis.add_buy_events(
        *process_buy_sell_events(decomposed_log[log_events.BuyEvent]))
    vis.add_sell_events(
        *process_buy_sell_events(decomposed_log[log_events.SellEvent]))
    fig = vis.plot()
    fig.show()

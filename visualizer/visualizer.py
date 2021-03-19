from __future__ import annotations

import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import typing as tp
import bisect

from trading import TrendLine, Candle


def to_time(ts: int) -> datetime:
    return datetime.fromtimestamp(ts)


def timestamp_to_hhmm(ts: int) -> str:
    return to_time(ts).strftime('%H:%M')


def timestamp_to_full(ts: int) -> str:
    return to_time(ts).strftime('%m-%d %H:%M:%S')


class GraphicLayer:
    __red = '#EF4F41'
    __green = '#41EF4F'
    __blue = '#4F41EF'
    __gray = '#787778'

    def __init__(self, visualizer: Visualizer, ts: int):
        self.visualizer = visualizer
        self.ts = ts
        self.left_candle_trace = None
        self.right_candle_trace = None
        self.buy_trace = None
        self.sell_trace = None
        self.trend_traces: tp.List[go.Scatter] = []
        self.ma_traces: tp.List[go.Scatter] = []
        self.ts_line = go.Scatter(visible=False,
                                  x=[to_time(ts), to_time(ts)],
                                  y=[visualizer._y_min, visualizer._y_max],
                                  mode='lines',
                                  line=dict(
                                      dash='dash',
                                      color=self.__gray,
                                      width=2,
                                  ),
                                  name=f'Time: {timestamp_to_full(self.ts)}')

    def add_candles(self, candle_params: tp.Dict[str, tp.List[tp.Any]],
                    prefix_len: int) -> None:
        self.left_candle_trace = go.Candlestick(
            visible=prefix_len == 0,
            x=[to_time(ts) for ts in
               candle_params['ts'][:prefix_len]],
            open=candle_params['open'][:prefix_len],
            high=candle_params['high'][:prefix_len],
            low=candle_params['low'][:prefix_len],
            close=candle_params['close'][:prefix_len],
            increasing=dict(
                line=dict(
                    color=self.__green
                )
            ),
            decreasing=dict(
                line=dict(
                    color=self.__red
                )
            ),
            showlegend=True,
            name='history WAVES/USDN'  # TODO: normal title
        )
        self.right_candle_trace = go.Candlestick(
            visible=prefix_len == 0,
            x=[to_time(ts) for ts in
               candle_params['ts'][prefix_len:]],
            open=candle_params['open'][prefix_len:],
            high=candle_params['high'][prefix_len:],
            low=candle_params['low'][prefix_len:],
            close=candle_params['close'][prefix_len:],
            increasing=dict(
                line=dict(
                    color=self.__green
                )
            ),
            decreasing=dict(
                line=dict(
                    color=self.__red
                )
            ),
            showlegend=True,
            name='future WAVES/USDN'  # TODO: normal title
        )

    def add_trend_line(self, trend_line: TrendLine, trend_length: int = 30,
                       name_suffix: str = "") -> None:
        from_ts = self.ts - trend_length * 300  # TODO: deal with trend_length
        to_ts = self.ts + trend_length * 300
        timestamps = np.array([from_ts, to_ts])
        prices = trend_line.get_value_at(timestamps)
        trend_trace = go.Scatter(visible=False,
                                 x=[to_time(ts) for ts in timestamps],
                                 y=prices,
                                 mode='lines',
                                 name=name_suffix,
                                 line=dict(
                                     color=self.__blue,
                                     width=1,
                                 ))
        self.trend_traces.append(trend_trace)

    def add_moving_average(self, moving_averages: tp.List[float],
                           timestamps: tp.List[datetime],
                           window_size: int) -> None:
        color = px.colors.qualitative.Pastel[len(self.ma_traces)]
        ma_trace = go.Scatter(visible=False,
                              x=timestamps,
                              y=moving_averages,
                              mode='lines',
                              name=f'Moving Average {window_size}',
                              line=dict(color=color)
                              )
        self.ma_traces.append(ma_trace)

    def add_buy_events(self, timestamps: tp.List[int], prices: tp.List[float],
                       amount: tp.List[float], meta: tp.List[str]) -> None:
        self.buy_trace = go.Scatter(visible=False,
                                    x=[to_time(ts) for ts in timestamps],
                                    y=prices,
                                    mode='markers',
                                    name='buy',
                                    marker=dict(
                                        # size=[15 * am for am in amount],
                                        size=15,
                                        color='green',
                                        symbol='arrow-up'),
                                    text=meta)

    def add_sell_events(self, timestamps: tp.List[int], prices: tp.List[float],
                        amount: tp.List[float], meta: tp.List[str]) -> None:
        self.sell_trace = go.Scatter(visible=False,
                                     x=[to_time(ts) for ts in timestamps],
                                     y=prices,
                                     mode='markers',
                                     name='sell',
                                     marker=dict(
                                         # size=[10 * am for am in amount],
                                         size=15,
                                         color='red',
                                         symbol='arrow-down'),
                                     text=meta)

    def get_traces(self) -> tp.List[tp.Union[go.Scatter, go.Candlestick]]:
        return [self.ts_line, self.left_candle_trace, self.right_candle_trace,
                self.sell_trace, self.buy_trace,
                *self.trend_traces,
                *self.ma_traces]

    def get_visibility_params(self,
                              candles_history: tp.Optional[bool] = None,
                              candles_future: tp.Optional[bool] = None,
                              ts_line: tp.Optional[bool] = None,
                              trends: tp.Optional[bool] = None,
                              buy: tp.Optional[bool] = None,
                              sell: tp.Optional[bool] = None,
                              ma: tp.Optional[bool] = None,
                              default_visibility: bool = True) \
            -> tp.List[bool]:
        visibility = [default_visibility if ts_line is None else ts_line,
                      default_visibility if candles_history is None else
                      candles_history,
                      default_visibility if candles_future is None else
                      candles_future,
                      default_visibility if sell is None else sell,
                      default_visibility if buy is None else buy]
        for _ in range(len(self.trend_traces)):
            visibility.append(default_visibility if trends is None else trends)
        for _ in range(len(self.ma_traces)):
            visibility.append(default_visibility if ma is None else ma)
        return visibility


def _slice_candles_by_attrs(candles: tp.List[Candle]) \
        -> tp.Dict[str, tp.List[tp.Any]]:
    return {
        param: [
            float(candle.__getattribute__(param))
            for candle in candles
            if (float(candle.open) != 0 or float(candle.close) != 0)
        ]
        for param in ['ts', 'open', 'close', 'high', 'low']
    }


class Visualizer:
    __red = '#EF4F41'
    __green = '#41EF4F'
    __blue = '#4F41EF'
    __gray = '#787778'

    def __init__(self) -> None:
        self._candles: tp.List[Candle] = []
        self._candle_params: tp.Dict[str, tp.List[tp.Any]] = {}
        self._layers: tp.List[GraphicLayer] = []
        self._y_min: float = 0
        self._y_max: float = 0
        self._ts_min: datetime = to_time(0)
        self._ts_max: datetime = to_time(0)
        self._layout = go.Layout({
            'title': {
                'text': 'WAVES/USDN',
                'font': {
                    'size': 15
                }
            },
            'yaxis': {

            },
            'xaxis': {
                'showspikes': True,
                'spikethickness': 2,
                'spikedash': "dot",
                'spikecolor': "#999999",
                'spikemode': "across",
            },
        })

    def add_candles(self, candles: tp.List[Candle]) -> None:
        self._candles = candles
        self._candle_params = _slice_candles_by_attrs(candles)
        self.__init_params_from_candles()
        for i, candle in enumerate(candles):
            self.__add_layer(candle.ts)
            self._layers[i].add_candles(self._candle_params, i)

    def add_trend_lines(self,
                        trend_lines: tp.List[tp.Mapping[str, tp.Any]],
                        trend_length: int = 30) -> None:
        for event in trend_lines:
            lower_trend_line = event['lower_trend_line']
            upper_trend_line = event['upper_trend_line']
            ts = event['ts']
            ind = self.__get_ind_by_ts(ts)
            if len(self._layers[ind].trend_traces) > 0:
                self._layers[ind].trend_traces = []
            if upper_trend_line is not None:
                self._layers[ind].add_trend_line(upper_trend_line,
                                                 trend_length,
                                                 name_suffix="upper line")
            if lower_trend_line is not None:
                self._layers[ind].add_trend_line(lower_trend_line,
                                                 trend_length,
                                                 name_suffix="lower line")

    def add_moving_average(self,
                           moving_averages: tp.List[tp.Dict[str, tp.Any]],
                           window_size: int) -> None:
        averages = []
        timestamps = []
        for event in moving_averages:
            average_value = event['average_value']
            averages.append(average_value)
            ts = event['ts']
            timestamps.append(to_time(ts))
            ind = self.__get_ind_by_ts(ts)
            self._layers[ind].add_moving_average(averages, timestamps,
                                                 window_size)

    def add_buy_events(self, timestamps: tp.List[int], prices: tp.List[float],
                       amount: tp.List[float], meta: tp.List[str]) -> None:
        self.__add_buy_sell_events(timestamps, prices, amount, meta,
                                   is_buy=True)

    def add_sell_events(self, timestamps: tp.List[int], prices: tp.List[float],
                        amount: tp.List[float], meta: tp.List[str]) -> None:
        self.__add_buy_sell_events(timestamps, prices, amount, meta,
                                   is_buy=False)

    def get_layers(self) -> tp.List[GraphicLayer]:
        return self._layers

    def get_layout(self) -> go.Layout:
        return self._layout

    def plot(self) -> go.Figure:
        self.__add_ts_slider()
        traces: tp.List[tp.Union[go.Scatter, go.Candlestick]] = []
        for layer in self._layers:
            traces.extend(layer.get_traces())
        return go.Figure(data=traces, layout=self._layout)

    def __adjust_timestamps_and_price(self, timestamps: tp.List[int],
                                      prices: tp.List[float],
                                      is_buy: bool = False) -> None:
        for i, ts in enumerate(timestamps):
            timestamps[i] = self._candles[self.__get_ind_by_ts(ts)].ts
        amount: tp.Dict[int, int] = {}
        shift = 0.05
        for i, ts in enumerate(timestamps):
            if ts not in amount:
                amount[ts] = 0
            else:
                amount[ts] += 1
            candle_id = self.__get_ind_by_ts(ts)
            if is_buy:
                prices[i] = self._candles[candle_id].get_lower_price() - \
                            amount[ts] * shift
            else:
                prices[i] = self._candles[candle_id].get_upper_price() + \
                            amount[ts] * shift

    def __add_buy_sell_events(self, timestamps: tp.List[int],
                              prices: tp.List[float], amount: tp.List[float],
                              meta: tp.List[str],
                              is_buy: bool = False) -> None:
        self.__adjust_timestamps_and_price(timestamps, prices, is_buy)
        current_layer = 0
        for i, ts in enumerate(timestamps):
            while current_layer < len(self._layers) and \
                    ts > self._layers[current_layer].ts:
                if is_buy:
                    self._layers[current_layer].add_buy_events(timestamps[:i],
                                                               prices[:i],
                                                               amount[:i],
                                                               meta[:i])
                else:
                    self._layers[current_layer].add_sell_events(timestamps[:i],
                                                                prices[:i],
                                                                amount[:i],
                                                                meta[:i])
                current_layer += 1
        for i in range(current_layer, len(self._layers)):
            if is_buy:
                self._layers[i].add_buy_events(timestamps,
                                               prices,
                                               amount,
                                               meta)
            else:
                self._layers[i].add_sell_events(timestamps,
                                                prices,
                                                amount,
                                                meta)

    def __add_layer(self, ts: int) -> None:
        self._layers.append(GraphicLayer(self, ts))

    def __add_ts_slider(self) -> None:
        steps = []
        for i, candle in enumerate(self._candles):
            step = dict(
                method="update",
                args=[{"visible": []},
                      {"title": "Trends at moment " + timestamp_to_full(
                          candle.ts)}],
                label=timestamp_to_hhmm(candle.ts)
            )
            for j, layer in enumerate(self._layers):
                step["args"][0]["visible"].extend(  # type: ignore
                    layer.get_visibility_params(default_visibility=(i == j)))
            steps.append(step)

        sliders = [dict(
            active=0,
            currentvalue={"prefix": "Time: "},
            pad={"t": 170},
            steps=steps
        )]
        self._layout['sliders'] = sliders

    def __get_ind_by_ts(self, ts: int) -> int:
        return bisect.bisect_right(self._timestamps, ts) - 1

    def __init_params_from_candles(self) -> None:
        self._timestamps = self._candle_params['ts']
        self._y_min = min(self._candle_params['low'])
        self._y_max = max(self._candle_params['high'])
        height = self._y_max - self._y_min
        self._y_min -= min(0.5 * height, 0.3)
        self._y_max += min(0.5 * height, 0.3)
        self._ts_min = to_time(self._candles[0].ts)
        self._ts_max = to_time(self._candles[-1].ts)
        self._layout.yaxis.range = (self._y_min, self._y_max)
        self._layout.xaxis.range = (self._ts_min, self._ts_max)

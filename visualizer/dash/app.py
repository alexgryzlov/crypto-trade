import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

import plotly.graph_objects as go

import sys

sys.path.append('.')

import visualizer.visualize_log as log
from visualizer.visualizer import Visualizer
from pathlib import Path
from logger.object_log import PATH_TO_DUMPS

import typing as tp

vis: tp.Optional[Visualizer] = None
log_path_opt = log.get_log_path()
log_path: tp.Optional[str] = None
if log_path_opt is not None:
    log_path = log_path_opt.name

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.Table([
        html.Tr([
            html.Th(html.Label('Candles'), style={'width': '30%'}),
            html.Th(html.Label('Indicators'), style={'width': '30%'}),
            html.Th(html.Label('Log'), style={'width': '30%'})
        ]),
        html.Tr([
            html.Td([
                dcc.Checklist(
                    id='candles-checklist',
                    options=[
                        {'label': 'Show future', 'value': 'FUT'},
                    ],
                    value=[]
                )
            ]),
            html.Td([
                dcc.Checklist(
                    id='indicators-checklist',
                    options=[
                        {'label': 'Moving Average', 'value': 'MA'},
                        {'label': 'Trend Lines', 'value': 'T'},
                        {'label': 'Buy/Sell Events', 'value': 'B/S'}
                    ],
                    value=['MA', 'T', 'B/S']
                )
            ]),
            html.Td([
                html.Div(
                    dcc.Input(id='log-filename-box', type='text',
                              value=log_path, style={'width': '100%'}),
                ),
                html.Div(
                    [html.Button('Load log', id='load-log-button'),
                     html.Button('Load last log', id='load-last-log-button')]
                )
            ])
        ])
    ], style={'width': '100%'}),
    html.Div([
        dcc.Graph(id='candlestick-chart', style={'height': '90%'}),
        dcc.Slider(id='timestamp-slider', updatemode='drag'),
    ], style={'height': '100%'})
], style={'height': '80vh'})


@app.callback(
    [Output('timestamp-slider', 'min'),
     Output('timestamp-slider', 'max'),
     Output('timestamp-slider', 'value')],
    [Input('load-log-button', 'n_clicks')],
    [State('log-filename-box', 'value')])
def update_log(n_clicks: tp.Optional[int],
               value: tp.Optional[str]) -> tp.Tuple[int, int, int]:
    if value is None or value == log_path:
        raise PreventUpdate

    reload_candlestick_from(value)
    if vis is None:
        raise PreventUpdate
    layers = vis.get_layers()
    return 0, len(layers), len(layers) // 2


@app.callback(
    [Output('timestamp-slider', 'min'),
     Output('timestamp-slider', 'max'),
     Output('timestamp-slider', 'value'),
     Output('log-filename-box', 'value')],
    [Input('load-last-log-button', 'n_clicks')])
def update_last_log(n_clicks: tp.Optional[int]) \
        -> tp.Tuple[int, int, int, str]:
    current_last_log = log.get_log_path()
    if current_last_log is None:
        raise PreventUpdate
    if current_last_log.name != log_path:
        reload_candlestick_from(current_last_log.name)
    if vis is None:
        raise PreventUpdate
    layers = vis.get_layers()
    return 0, len(layers), len(layers) // 2, tp.cast(str, log_path)


@app.callback(Output('candlestick-chart', 'figure'),
              [Input('timestamp-slider', 'value'),
               Input('indicators-checklist', 'value'),
               Input('candles-checklist', 'value')])
def update_candlestick_chart(timestamp: int, indicators: tp.List[str],
                             candles_future: tp.List[str]) -> go.Figure:
    global vis
    if vis is None or timestamp is None:
        raise PreventUpdate
    layers = vis.get_layers()
    layer = layers[timestamp]
    traces = layer.get_traces()
    visibility = layer.get_visibility_params(
        candles_future='FUT' in candles_future,
        ma='MA' in indicators,
        trends='T' in indicators,
        buy='B/S' in indicators,
        sell='B/S' in indicators
    )
    layout = vis.get_layout()
    for trace, visible in zip(traces, visibility):
        trace['visible'] = visible
    fig = go.Figure(data=traces, layout=layout)
    fig.update_yaxes(automargin=True)
    return fig


def reload_candlestick_from(new_log_path: str) -> None:
    global vis, log_path
    log_path = new_log_path
    decomposed_log = load_log(new_log_path)
    vis = log.create_visualizer_from_log(decomposed_log)


def load_log(filename: str) -> tp.Dict[tp.Any, tp.List[tp.Any]]:
    path = Path(PATH_TO_DUMPS.joinpath(filename))
    if not path.is_file():
        path_opt = log.get_log_path()
        if path_opt is None:
            raise PreventUpdate
        path = path_opt
    if path is None:
        raise RuntimeError('Incorrect path to log')
    print(path)
    logs = log.load_log(path)
    return log.decompose_log(logs)


if __name__ == '__main__':
    if log_path is None:
        print('Log not found')
        exit(0)
    reload_candlestick_from(log_path)
    app.run_server(debug=True)

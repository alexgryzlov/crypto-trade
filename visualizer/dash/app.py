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
from logger.logger import Logger

import typing as tp

vis: tp.Optional[Visualizer] = None
log_path_opt = log.get_log_path()
log_path: tp.Optional[str] = None
if log_path_opt is not None:
    log_path = log_path_opt.name
load_last_log_clicks = 0

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.Table([
        html.Tr([
            html.Th(html.Label('General'), style={'width': '10%'}),
            html.Th(html.Label('Indicators'), style={'width': '60%'}),
            html.Th(html.Label('Log'), style={'width': '30%'})
        ]),
        html.Tr([
            html.Td([
                dcc.Checklist(
                    id='general-checklist',
                    options=[
                        {'label': 'Show future', 'value': 'FUT'},
                        {'label': 'Buy/Sell Events', 'value': 'B/S'}
                    ],
                    value=['B/S']
                )
            ]),
            html.Td([
                html.Div(
                    dcc.Checklist(
                        id='indicators-checklist-0',
                        options=[
                            {'label': 'Trend Lines', 'value': 'T'}
                        ],
                        value=['T'],
                        labelStyle={'display': 'block'}
                    ),
                    style={'width': '20%', 'height': '100%', 'float': 'left'},
                ),
                html.Div(
                    dcc.Checklist(
                        id='indicators-checklist-1',
                        options=[],
                        value=[],
                        labelStyle={'display': 'block'}
                    ),
                    style={'width': '20%', 'height': '100%', 'float': 'left'},
                ),
                html.Div(
                    dcc.Checklist(
                        id='indicators-checklist-2',
                        options=[],
                        value=[],
                        labelStyle={'display': 'block'}
                    ),
                    style={'width': '20%', 'height': '100%', 'float': 'left'},
                ),
                html.Div(
                    dcc.Checklist(
                        id='indicators-checklist-3',
                        options=[],
                        value=[],
                        labelStyle={'display': 'block'}
                    ),
                    style={'width': '20%', 'height': '100%', 'float': 'left'},
                ),
                html.Div(
                    dcc.Checklist(
                        id='indicators-checklist-4',
                        options=[],
                        value=[],
                        labelStyle={'display': 'block'}
                    ),
                    style={'width': '20%', 'height': '100%', 'float': 'left'},
                ),
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

CheckLst = tp.List[tp.Dict[str, str]]


@app.callback(
    [Output('timestamp-slider', 'min'),
     Output('timestamp-slider', 'max'),
     Output('timestamp-slider', 'value'),
     Output('log-filename-box', 'value'),
     Output('indicators-checklist-0', 'options'),
     Output('indicators-checklist-1', 'options'),
     Output('indicators-checklist-2', 'options'),
     Output('indicators-checklist-3', 'options'),
     Output('indicators-checklist-4', 'options'),
     ],
    [Input('load-log-button', 'n_clicks'),
     Input('load-last-log-button', 'n_clicks')],
    [State('log-filename-box', 'value')])
def update_log(n_log_clicks: tp.Optional[int],
               n_last_log_clicks: tp.Optional[int],
               value: tp.Optional[str]) -> tp.Tuple[int, int, int, str,
                                                    CheckLst, CheckLst,
                                                    CheckLst, CheckLst,
                                                    CheckLst]:
    global load_last_log_clicks
    if n_last_log_clicks is not None and \
            n_last_log_clicks > load_last_log_clicks:
        load_last_log_clicks = n_last_log_clicks
        current_last_log = log.get_log_path()
        if current_last_log is None:
            raise PreventUpdate
        value = current_last_log.name
    if value is None:
        raise PreventUpdate

    curves = reload_candlestick_from(value)
    chks = generate_indicators_options(curves)
    if vis is None:
        raise PreventUpdate
    layers = vis.get_layers()
    return 0, len(layers), len(layers) // 2, value, chks[0], chks[1], chks[2], \
           chks[3], chks[4]


@app.callback(Output('candlestick-chart', 'figure'),
              [Input('timestamp-slider', 'value'),
               Input('indicators-checklist-0', 'value'),
               Input('indicators-checklist-1', 'value'),
               Input('indicators-checklist-2', 'value'),
               Input('indicators-checklist-3', 'value'),
               Input('indicators-checklist-4', 'value'),
               Input('general-checklist', 'value')])
def update_candlestick_chart(timestamp: int, ind1: tp.List[str],
                             ind2: tp.List[str], ind3: tp.List[str],
                             ind4: tp.List[str], ind5: tp.List[str],
                             general_info: tp.List[str]) -> go.Figure:
    indicators = [*ind1, *ind2, *ind3, *ind4, *ind5]
    global vis
    if vis is None or timestamp is None:
        raise PreventUpdate
    layers = vis.get_layers()
    timestamp = min(timestamp, len(layers) - 1)
    layer = layers[timestamp]
    traces = layer.get_traces()
    visibility = layer.get_visibility_params(
        candles_future='FUT' in general_info,
        trends='T' in indicators,
        buy='B/S' in general_info,
        sell='B/S' in general_info,
        indicators=indicators
    )
    layout = vis.get_layout()
    for trace, visible in zip(traces, visibility):
        trace['visible'] = visible
    fig = go.Figure(data=traces, layout=layout)
    fig.update_yaxes(automargin=True)
    return fig


def generate_indicators_options(labels: tp.List[str]) \
        -> tp.Tuple[
            CheckLst, CheckLst, CheckLst,
            CheckLst, CheckLst]:
    base = [
        {'label': 'Trend Lines', 'value': 'T'}
    ]
    base.extend({'label': label, 'value': label} for label in sorted(labels))
    columns: tp.List[CheckLst] = []
    step = 3
    for i, _ in zip(range(0, len(base), step), range(5)):
        columns.append(base[i:i + step])
    for i in range(len(columns), 5):
        columns.append([])
    return columns[0], columns[1], columns[2], columns[3], columns[4]


def reload_candlestick_from(new_log_path: str) -> tp.List[str]:
    global vis, log_path
    log_path = new_log_path
    decomposed_log = load_log(new_log_path)
    current_curves = log.get_all_curve_names(decomposed_log)
    vis = log.create_visualizer_from_log(decomposed_log)
    return current_curves


def load_log(filename: str) -> log.DecomposedLogType:
    path = Path(Logger.get_logs_path('dump') / filename)
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

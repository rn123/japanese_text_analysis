# -*- coding: utf-8 -*-
from _plotly_future_ import v4_subplots
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from dash.dependencies import Input, Output
from plotly.subplots import make_subplots

import numpy as np

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

attentions = np.load('attentions.npy')

with open('three_character_text_phebe.txt') as fp:
    text = fp.read()

text = text.split('\n')

with open('tokens.txt') as fp:
    tokens = fp.read()

tokens = tokens.split('\n')

app.layout = html.Div(style={'backgroundColor': colors['background']}, 
    children=[
        html.H1(
            children='Hello Dash',
            style={
                'textAlign': 'center',
                'color': colors['text']
            }
        ),

        html.Div(
            children='Dash: A web application framework for Python.', 
            style={
                'textAlign': 'center',
                'color': colors['text']
            }
        ),

        html.Div([
            dcc.Dropdown(
                id='text-dropdown',
                options=[ {'label':t, 'value':idx} for idx,t in enumerate(text)],
                value='5'
            )], style={'width': '30%', 'display': 'inline-block'}
        ),

        html.Div([
            dcc.Slider(
                id='layer-slider',
                min=1,
                max=12,
                marks={i: 'Layer {}'.format(i) if i == 1 else str(i) for i in range(1, 13)},
                value=5,
            )], style={'width': '35%', 'display': 'inline-block'}
        ),

        html.Div([
            dcc.Slider(
                id='head-slider',
                min=1,
                max=12,
                marks={i: 'Head {}'.format(i) if i == 1 else str(i) for i in range(1, 13)},
                value=5,
            )], style={'width': '35%', 'float': 'right', 'display': 'inline-block'}
        ),

        html.Div([
            dcc.Graph(
                id='attentions-heatmap',
                figure={
                    'data': [
                        {'x':tokens[0], 'y':tokens[0], 'z':attentions[0][10][0][9], 'type':'heatmap'}
                    ],
                    'layout': {
                        'plot_bgcolor': colors['background'],
                        'paper_bgcolor': colors['background'],
                        'font': {
                            'color': colors['text']
                        }
                    }
                }
            )
        ], style={'width': '48%', 'display': 'inline-block'}),

        html.Div([
            dcc.Graph(
                id='attentions-map',
                figure=make_subplots(specs=[[{"secondary_y": True}]])
            )
        ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'}),       
    ]
)

@app.callback(
    Output('attentions-heatmap', 'figure'),
    [Input('text-dropdown', 'value'),
     Input('layer-slider', 'value'),
     Input('head-slider', 'value')]
)
def update_heatmap(text_idx, layer_value, head_value):
    text_id = text_idx
    layer = layer_value
    batch_value = 0
    head = head_value
    traces = []
    traces.append(dict(
        z = attentions[text_id][layer - 1][batch_value][head - 1],
        x = tokens[text_id].split(),
        y = tokens[text_id].split(),
        type = 'heatmap',
        hoverongaps = False
        )
    )

    return {
        'data': traces,
        'layout': dict()
    }

@app.callback(
    Output('attentions-map', 'figure'),
    [Input('text-dropdown', 'value'),
     Input('layer-slider', 'value'),
     Input('head-slider', 'value')]
)
def update_map(text_idx, layer_value, head_value):
    text_id = text_idx
    layer = layer_value
    batch_value = 0
    head = head_value
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    z = attentions[text_id][layer - 1][batch_value][head - 1]
    data = [(m, n, 2*float(z[mi,ni])) 
            for ni, n in enumerate(tokens[text_id].split()) 
            for mi, m in enumerate(tokens[text_id].split())
            ]

    for d in data:
        fig.add_trace(go.Scattergl(
                x = [0, 1],
                y = [d[0], d[1]],
                line = {'width':d[2], 'color':'blue'},
                showlegend = False),
                secondary_y = False
        )   
    for d in data:
        fig.add_trace(go.Scattergl(
                x = [0, 1],
                y = [d[0], d[1]],
                line = {'width':d[2], 'color':'blue'},
                showlegend = False),
                secondary_y = True
        )

    fig.layout.xaxis.showgrid = False
    fig.layout.xaxis.zeroline = False
    fig.layout.xaxis.showticklabels = False
    fig.layout.yaxis.showgrid = False
    fig.layout.yaxis2.showgrid = False
    print(fig.layout)

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)

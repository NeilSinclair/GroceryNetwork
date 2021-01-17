import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import plotly.offline as py
import plotly.graph_objects as go

import networkx as nx

import pickle
import collections
import pandas as pd

from utils import *

########### Initiate the app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
application = app.server
app.title='Groceries on a graph'

pos, G = load_graph()

node_trace, edge_trace = create_graph_display(G, pos)

########### Set up the layout

## Layout comprises two tabs - one for viewing of the graph and the other for making a shopping list
# Get the name of the tabs, and their associated id

app.layout = html.Div([
    dcc.Tabs(id='tabs-example', value='tab-1', children=[
        dcc.Tab(label='Tab one', value='tab-1'),
        dcc.Tab(label='Tab two', value='tab-2'),
    ]),
    html.Div(id='tabs-example-content')
])

@app.callback(Output('tabs-example-content', 'children'),
              Input('tabs-example', 'value'))
def render_content(value):
    if value == 'tab-1':
        return display_network_graph()
    elif value == 'tab-2':
        return display_shopping_list()


# app.layout = html.Div([
#     html.H1('Grocery Graph Network'),
#     html.Div(
#         children=[
#                 dcc.Tabs(id='tabs', value='tab2', children=[
#                     dcc.Tab(label='Network Graph', value='tab1'),
#                     dcc.Tab(label='Shopping List Creator', value='tab2')
#                 ]
#             )
#         ],
#         ),
#     # This is the output of the tab - i.e. the page selected
#     html.Div(id='tab_output')
# ])
#
# @app.callback(dash.dependencies.Output('tab_output', 'children'),
#               dash.dependencies.Input('tabs', 'value'))
# def display_tab(value):
#     # print(value)
#     if value == 'tab1':
#         return display_network_graph()
#     else:
#         return display_shopping_list()

# def display_network_graph():
#     ''' Function that displays the network tab'''
#     graph = dcc.Graph(id='graph-graphic'),
#
#     slider = dcc.Slider(
#         id='min-edges-slider',
#         min=5,
#         max=20,
#         value=10,
#         step=None,
#         # marks = {1:'1 edge', 2:'2 edges', 3:'3 edges', 4:'4 edges', 5: '5 edges',
#         #          6:'6 edge', 7:'7 edges', 8:'8 edges', 9:'9 edges', 10: '10 edges'}
#         marks = {5:'5 edges', 10:'10 edges', 15:'15 edges', 20:'20 edges', 25: '25 edges'}
#     )
#     return html.Div(children=[graph, slider])

def display_shopping_list():
    return html.Div(children=[
        html.H3('Tab content 2')
    ])

def display_network_graph():
    return html.Div(children=[
        html.H3('Tab content 1')
    ])


@app.callback(
    Output('graph-graphic', 'figure'),
    Input('min-edges-slider', 'value')
)
def update_graph(min_edges):
    pos, G = load_graph(min_edges)

    node_trace, edge_trace = create_graph_display(G, pos)

    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        title='<br>Graph of shopping cart items',
                        titlefont_size=16,
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=20, l=5, r=5, t=40),
                        annotations=[dict(
                            text="some text",
                            showarrow=False,
                            xref="paper", yref="paper",
                            x=0.005, y=-0.002)],
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )
    return fig

########### Run the app
if __name__ == '__main__':
    application.run(debug=True, port=8080)
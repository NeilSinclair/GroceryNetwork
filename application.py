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
dict_tabs={
    "Network Graph":"tab1",
    "Shopping List":"tab2"
}

app.layout = html.Div([
    html.H1('Grocery Graph Network'),
    dcc.Graph(id='graph-graphic'),

    dcc.Slider(
        id='min-edges-slider',
        min=5,
        max=20,
        value=10,
        step=None,
        # marks = {1:'1 edge', 2:'2 edges', 3:'3 edges', 4:'4 edges', 5: '5 edges',
        #          6:'6 edge', 7:'7 edges', 8:'8 edges', 9:'9 edges', 10: '10 edges'}
        marks = {5:'5 edges', 10:'10 edges', 15:'15 edges', 20:'20 edges', 25: '25 edges'}
    )
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
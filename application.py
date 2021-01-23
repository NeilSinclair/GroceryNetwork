import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
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
list_dict = [{}]
## Load an initial Graph ##
with open('med_graph.pickle', 'rb') as f:
    G_init = pickle.load(f)
nodes = list(G_init.nodes)
########### Set up the layout

## Layout comprises two tabs - one for viewing of the graph and the other for making a shopping list
# Get the name of the tabs, and their associated id

app.layout = html.Div([
    html.H1('Grocery Graph Network'),
    html.Div([
    ## Show the tabgs
    dcc.Tabs(id='tabs-example', value='tab-2', children=[
        dcc.Tab(label='Network Graph', value='tab-1'),
        dcc.Tab(label='Shopping List Builder', value='tab-2'),
        ]
        )
    ]
    ),
    html.Div(id='tabs-output')
])

@app.callback(Output('tabs-output', 'children'),
              Input('tabs-example', 'value'))
def render_content(value):
    if value == 'tab-1':
        return display_network_graph()
    elif value == 'tab-2':
        return display_shopping_list()




def display_network_graph():
    ''' Function that displays the network tab'''

    # Setup a div for the inputs to the graph
    dd_segment = dcc.Dropdown(
        id='dd_segment',
        className='dropdown',
        options=[{'label': 'Small', 'value': 0},
                 {'label': 'Medium', 'value': 1}],
        value=0
    )

    input_settings = html.Div([
        html.Div(className='row', children=[
                    html.Div(className='col',
                        children=[
                            html.H4("Select Segment"),
                            dd_segment
                        ],
                        style={'width': '30%', 'display': 'inline-block'}
                    )
            ]),
         html.Div(className='row', children=[
                    html.Div(children=[
                        dcc.Graph(id='graph-graphic')
                    ])
                  ])
    ])

    return input_settings

def display_shopping_list():
    return html.Div([
        html.Div(className='row', children=[
            html.Div(className='col', children=[
                html.P("Here is some text explaining what happens here")
            ])
        ]),
        html.Div(className='row', children=[
            html.Div(className='col', children=[
                html.Div(className='row', children=[
                    # Search box in here
                    html.H3("Search items"),
                    dcc.Input(
                        id='item_search',
                        type='search',
                        placeholder='Search Shopping Items',
                        debounce=False,
                        value='Search Shopping Items'
                    )

                ], style={'display': 'inline-block'}
                ),
                html.Div(className='row', children=[
                    html.P("Placeholder for search box"),
                    dcc.Checklist(
                        id='item_checklist',
                        options=list_dict,
                      )
                ], style={'display': 'inline-block'})
            ],
            style={'width': '50%', 'display': 'inline-block'}
            ),
            html.Div(className='col', children=[
                html.Div(className='row', children=[
                    # Search box in here
                    html.H3("Your Shopping List")
                ], style={'display': 'inline-block'}),
                html.Div(className='row', children=[
                    # Selectable search items go in here
                    html.P("Placeholder for shopping list")
                ], style={'display': 'inline-block'})
            ],
             style={'width': '50%', 'display': 'inline-block'}
             )

        ])
    ])


@app.callback(
    Output('item_checklist', 'options'),
    [Input('item_search', 'value')]
)
def update_items(item):
    shopping_items = find_ingredient(nodes, item)
    checklist = []
    for it in shopping_items:
        checklist.append({'label': it,
                          'value': it})
    # list_dict = checklist

    return checklist

@app.callback(
    Output('graph-graphic', 'figure'),
    [Input('dd_segment', 'value')]
)
def update_graph(segment):

    pos, G = load_graph(segment=segment)

    node_trace, edge_trace = create_graph_display(G, pos)

    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        title='',
                        titlefont_size=16,
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=20, l=5, r=5, t=40),
                        annotations=[dict(
                            text="",
                            showarrow=False,
                            xref="paper", yref="paper",
                            x=0.005, y=-0.002)],
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )
    nodes = G.nodes
    return fig

########### Run the app
if __name__ == '__main__':
    application.run(debug=True, port=8080)
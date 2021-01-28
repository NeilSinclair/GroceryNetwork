import dash
import dash_core_components as dcc
import dash_html_components as html

from dash.dependencies import Input, Output, State, MATCH, ALL

import re

from utils import *

########### Initiate the app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
# app = dash.Dash('Grocery Recommender')
# for source in ["https://codepen.io/jeanmidevacc/pen/paxKzB.css","https://codepen.io/pixinema/pen/XZvJyX.css"]:
#     app.css.append_css({"external_url": source})
application = app.server
app.title='Groceries on a graph'
list_dict = [{}]
## Load an initial Graph ##
with open('large_graph.pickle', 'rb') as f:
    G_init = pickle.load(f)
nodes = list(G_init.nodes)

## Create an empty set of buttons


class ButtonInputs():
    def __init__(self, names, ids):
        self.names = names
        self.ids = ids
        self.inputs = list()

    def get_inputs(self):
        # for name, id in zip(self.names, self.ids):
        for id in self.ids:
            self.inputs.append(Input(id, 'n_clicks'))

        return self.inputs

########### Set up the layout

tabs_styles = {
    'height': '44px'
}
tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '6px',
    'fontWeight': 'bold'
}

tab_selected_style = {
    'borderTop': '0px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': '#1a1a1a',
    'color': 'white',
    'padding': '6px'
}

## Layout comprises two tabs - one for viewing of the graph and the other for making a shopping list
# Get the name of the tabs, and their associated id

app.layout = html.Div([
    html.Div(className='row', children=[
        html.H1(children='Grocery Graph Network')
        ], style={'textAlign': 'center',
                  'backgroundColor': '#1a1a1a',
                  'color': 'white'}),
    html.Div([
    ## Show the tags
    dcc.Tabs(id='tabs-example', value='tab-1',
             # parent_className='custom-tabs',
             # className='custom-tabs-container',
             children=[
        dcc.Tab(label='Shopping List Builder', value='tab-1',
                style=tab_style,
                selected_style=tab_selected_style),
        dcc.Tab(label='Explore Network Graph', value='tab-2',
                style=tab_style,
                selected_style=tab_selected_style)
        ], style=tabs_styles
        )
    ]
    ),
    html.Div(id='tabs-output')
])

@app.callback(Output('tabs-output', 'children'),
              Input('tabs-example', 'value'))
def render_content(value):
    if value == 'tab-2':
        return display_network_graph()
    elif value == 'tab-1':
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
                            html.P("Select either a segment, named according to basket size"),
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
            html.Div(className='six columns', children=[
                html.Div(className='row', children=[
                    # Search box in here
                    html.H3("Search items"),
                    dcc.Input(
                        id='item_search',
                        type='search',
                        placeholder='Search Shopping Items',
                        debounce=True,
                        value='Apples'
                    ),
                    html.P(""),
                    html.P(id='explainer',
                           children=["The items below are the closest that match your search"]),
                    html.P("")
                ]
                ),
                 html.Div(className='row', id='button-container', children=[]

            )],
            ),
            html.Div(className='six columns', children=[
                html.Div(className='row', children=[
                    html.Div(className='six columns', children=[html.H3("Your Shopping List")])
                ]),
                # Dyanamic shopping list is built here
                html.Div(className='row', id='shopping-list-container', children=[]
                    )
                ],

             )

        ])
    ])

@app.callback(
    Output('button-container', 'children'),
    Output('shopping-list-container', 'children'),
    Output('explainer', 'children'),
    [Input('item_search', 'value'),
    Input({'type': 'button', 'index': ALL}, 'n_clicks')],
    [State('button-container', 'children'),
    State('shopping-list-container', 'children'),
    State('explainer', 'children')]
)
def display_search_buttons(item, vals, buttons, shopping_list_items, explainer_text):
    ctx = dash.callback_context
    # Make the text in the same format as the itmes
    item = item.title()
    shopping_items = find_ingredient(nodes, item)
    print(f'ctx.triggered[0]["value"] is None: {ctx.triggered[0]["value"] is None}')
    buttons = []
    for i, it in enumerate(shopping_items):
        new_button = html.Button(
            f'{it}',
            id={'type': 'button',
                'index': it
            },
            n_clicks=0
        )
        buttons.append(new_button)
        explainer_text = r"""The items below are the closest that match your search"""

    # Check the button was clicked at least once
    if ctx.triggered and ctx.triggered[0]['value'] != 0 and ctx.triggered[0]['prop_id'] != 'item_search.value':
        # Get the name of the grocery item
        button_clicked = re.findall(r':"(.*?)"', ctx.triggered[0]['prop_id'])[0]
        # Add it to the shopping list
        new_item = html.P(
            f'{button_clicked}'
        )
        shopping_list_items.append(new_item)

        # Erase the list of ingredients and present similar ingredients by searching the graph
        buttons = []
        recommendations = traverse_graph(G_init, button_clicked, 15, cutoff=1, random_=True)
        # Update the explainer so the user knows what's going on
        explainer_text = r"""You're now being shown similar items to what you just added. If you'd like to search for  
                         something specific, use the search bar again"""
        # Add the recommended items to the buttons for adding to the shopping list
        for i, it in enumerate(recommendations[1:]):
            new_button = html.Button(
                f'{it}',
                id={'type': 'button',
                    'index': it
                    },
                n_clicks=0
            )
            buttons.append(new_button)

    return buttons, shopping_list_items, explainer_text




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
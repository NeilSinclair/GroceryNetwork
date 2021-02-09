import dash
import dash_core_components as dcc
import dash_html_components as html

from dash.dependencies import Input, Output, State, ALL

import re

from utils import *

########### Initiate the app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

application = app.server
app.title='Groceries on a graph'
list_dict = [{}]
## Load an initial Graph ##
with open('large_graph.pickle', 'rb') as f:
    G_init = pickle.load(f)
nodes = list(G_init.nodes)

## Create a global button tracker
BUTTON_CLICKED = None

button_style = {'margin-right': '5px',
               'margin-left': '5px',
               'margin-top': '5px',
               'margin-bottom': '5px'}

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
    ## Show the tabs
    dcc.Tabs(id='tabs-example', value='tab-1',
             children=[
        dcc.Tab(label='Explore Network Graph', value='tab-1',
                style=tab_style,
                selected_style=tab_selected_style),
         dcc.Tab(label='Shopping List Builder', value='tab-2',
                 style=tab_style,
                 selected_style=tab_selected_style)
        ], style=tabs_styles
        )
    ]
    ),
    html.Div(id='tabs-output')
])

# Callback for selecting/changing tabs
@app.callback(Output('tabs-output', 'children'),
              Input('tabs-example', 'value'))
def render_content(value):
    if value == 'tab-1':
        return display_network_graph()
    elif value == 'tab-2':
        return display_shopping_list()



# Code for displaying the network graph
def display_network_graph():
    ''' Function that displays the network tab'''

    # Setup a dropdown menu for the inputs to the graph
    dd_segment = dcc.Dropdown(
        id='dd_segment',
        className='dropdown',
        options=[{'label': 'Small', 'value': 0},
                 {'label': 'Medium', 'value': 1}],
        value=0
    )
    # Create a div for the input settings, which includes the dropdown declared above
    input_settings = html.Div([
        html.Div(className='row', children=[
                    html.Div(className='col',
                        children=[
                            html.H4("Select Segment"),
                            html.P("Select a segment, named according to basket size"),
                            dd_segment
                        ],
                        style={'width': '30%', 'display': 'inline-block'}
                    )
            ]),
         # Display the main graph, with loading icon whilst loading
         html.Div(className='row', children=[
                    html.Div(children=[
                        dcc.Loading(id='loading-icon',
                                    children=[
                                        dcc.Graph(id='graph-graphic')
                                    ])
                    ])
                  ])
    ])

    return input_settings

# Code for displaying the items on the shopping recommender/list tab
def display_shopping_list():
    return html.Div([
        html.Div(className='row', children=[
            html.Div(className='col', children=[
                html.P("Description: Search for items to start building your shopping list. \
                Once you've selected an item, similar items will be recommended to you")
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
                        value='Pears'
                    ),
                    html.P(""),
                    # Radio items to choose how
                    html.P("Method for making recommendations: "),
                    dcc.RadioItems(id='sim-radio',
                                   options=[{'label': 'Similar', 'value': 'similar'},
                                            {'label': 'Neighbours', 'value': 'neighbours'}],
                                   value='similar',
                                   labelStyle={'display': 'inline-block'}),

                    html.P(""),
                    html.P(id='explainer',
                           children=["The items below are the closest that match your search"],
                           style={'font-weight': 'bold'}),
                    html.P("")
                ]
                ),
                 # Container that loads the items closest to what you searched for or
                 # recommended items
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
    Input({'type': 'button', 'index': ALL}, 'n_clicks'),
    Input('sim-radio', 'value')],
    [State('button-container', 'children'),
    State('shopping-list-container', 'children'),
    State('explainer', 'children')]
)
def display_search_buttons(item, vals, sim_val, buttons, shopping_list_items, explainer_text):
    ''' Function that runs all of the updates on for the shopping list'''
    ctx = dash.callback_context
    # Make the text in the same format as the times
    item = item.title()

    # If something has been triggered and it's the page loading or it's an item searched for
    # then load the items as per what was searched for
    if ctx.triggered is not None and \
            ctx.triggered[0]['prop_id'] == '.' or \
            ctx.triggered[0]['prop_id'] == 'item_search.value':
        buttons = []
        # Search for shopping items based on the item typed in the search bar
        # and create buttons
        shopping_items = find_ingredient(nodes, item)
        # Sort the items by length to make the display look nicer
        shopping_items.sort(key=len)
        counter = 0
        for i, it in enumerate(shopping_items):
            new_button = html.Button(
                f'{it}',
                id={'type': 'button',
                    'index': it
                },
                n_clicks=0,
                style=button_style
            )
            counter += 1
            buttons.append(new_button)
            # Stop too many items from being added
            if counter > 20:
                break
            explainer_text = r"""The items below are the closest that match your search"""

    # Check a button was clicked & that it's at least the first click (no auto clicks when the page loads)
    # & it's not the search input being searched in and it's not the radio button being checked
    elif ctx.triggered and ctx.triggered[0]['value'] != 0 and \
            ctx.triggered[0]['value'] is not None and \
            ctx.triggered[0]['prop_id'] != 'item_search.value' and \
            ctx.triggered[0]['prop_id'] != 'sim-radio.value':

        # Get the name of the grocery item
        button_clicked = re.findall(r':"(.*?)"', ctx.triggered[0]['prop_id'])[0]
        # track the button clicked for the next elif
        global BUTTON_CLICKED
        BUTTON_CLICKED = button_clicked
        # Add it to the shopping list
        new_item = html.P(
            f'{button_clicked}'
        )
        shopping_list_items.append(new_item)

        # Erase the list of ingredients and present similar ingredients by searching the graph
        buttons, explainer_text = recommend_groceries(button_clicked, sim_val)

    # Check if someone does something and if that something is changing the value on the
    # similarity measure radio button and
    elif ctx.triggered is not None and \
            BUTTON_CLICKED is not None and \
            ctx.triggered[0]['prop_id'] == 'sim-radio.value':
        buttons, explainer_text = recommend_groceries(BUTTON_CLICKED, sim_val)

    return buttons, shopping_list_items, explainer_text

def recommend_groceries(button_clicked, sim_val):
    ''' Function that returns a list of recommended groceries
    Args:  button_clicked - the button (item) clicked by the user
            sim_val - the type of similarity the user wants for recommendations
                    either 'similar' or 'neighbours'
    Returns: a list of recommended items for the user
    '''
    buttons = []
    # Get recommendations based on the similarity method chosen by the user
    if sim_val == "similar":
        recommendations = similar_embeddings(button_clicked, 10)
    else:
        recommendations = get_neighbours(G_init, button_clicked)
    # Update the explainer so the user knows what's going on
    explainer_text = r"""These items are recommended based on the last item added to your basket"""

    # Stop a system-hanging number of recommendations being added
    if len(recommendations) > 20:
        recommendations = recommendations[:20]
    # Sort the recommendations based on how many words each comprises; this makes the display
    # look nicer
    recommendations.sort(key=len)
    # Add the recommended items to the buttons for adding to the shopping list
    for i, it in enumerate(recommendations):
        new_button = html.Button(
            f'{it}',
            id={'type': 'button',
                'index': it
                },
            n_clicks=0,
            style=button_style
        )
        buttons.append(new_button)
    return buttons, explainer_text


# Callback for updating the graph network display when the user changes the segment size that
# they're looking at
@app.callback(
    Output('graph-graphic', 'figure'),
    [Input('dd_segment', 'value')]
)
def update_graph(segment):
    ''' Function to load a pre-computed graph network based on the segment selected by
        the user in the dropdown
    Args:   segment - the segment selected by the user in the dropdown
    '''
    # Load the graph data and create the nodes and elements needed for display
    pos, G = load_graph(segment=segment)

    node_trace, edge_trace = create_graph_display(G, pos)
    # Display the graph
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

    return fig

########### Run the app
if __name__ == '__main__':
    application.run(debug=True, port=8080)
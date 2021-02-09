import random
import networkx as nx
import pickle
import numpy as np

import plotly.graph_objects as go
import gensim

### Load the embedder object; note this is presaved/pre-computed
with open('embedder_weighted.pickle', 'rb') as f:
    embedder = pickle.load(f)

def similar_embeddings(source_node, topn):
    ''' Function that returns the top ncounts most similar items using embeddings'''
    most_similar = embedder.wv.most_similar(source_node, topn=topn)
    return [i[0] for i in most_similar]

# Traverse the graph by selecting the most weighted item
def get_neighbours(G, item, topn=10):
    ''' Function that returns the neighbours of a node
    Args: G - the netwowrkx Graph object
          item: the start node for searching -> str
          topn: number of neighbours to return -> int
    Returns: a list of grocery items occuring in a basket together
    '''

    # items = list(G.neighbors(item))
    weights = {}
    # Get all the neighbours of a node and sort them by their edge weight
    for nodes in list(G.edges(str(item))):
        weights[nodes[1]] = G.get_edge_data(nodes[0], nodes[1])['weight']
    weights_sorted = {k: v for k, v in sorted(weights.items(), key=lambda x: x[1], reverse=True)}
    # Filter so we just have the topn items
    items = list(weights_sorted.keys())[0:topn]

    return items


def find_ingredient(nodes, ingredient="Pear"):
    ''' Function that returns the closet match to an ingredient in the graph
    Args: ingredient: the ingredient you want to find -> str
          nodes: a list of the nodes in the graph -> list
    Returns: a list of the closest ingredients found
    '''
    ingredients = []

    for node in nodes:
        # This does a string-like search for the ingredient/item in each node
        # So ingredient="Pear" can return "Pear Jam", "Potato and Pear Soup" etc.
        if ingredient in node:
            ingredients.append(node)

    return ingredients


def load_graph(segment):
    ''' Function that creates the graph of the graph based on the min number of edges
    Args: segment: indicates which segment: 0, 1  to choose -> int
    Returns: graph and pos objects
    '''
    ### Load the data up
    segments = ['small_graph_v2.pickle', 'med_graph_v2.pickle']

    with open(segments[segment], 'rb') as f:
        G = pickle.load(f)

    pos = nx.spring_layout(G)

    return pos, G

def create_graph_display(G, pos):
    ''' Function for displaying the graph; most of this code is taken
        from the Plotly site
    Args:   G - networkx graph object
            pos - positions of nodes
    '''
    nodes = [node for node in G.nodes()]

    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines')

    node_x = []
    node_y = []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        hoverinfo='text',
        hovertext="10",
        text="",
        textfont=dict(
            family="sans serif",
            size=11
        ),
        marker=dict(
            showscale=True,
            colorscale='YlGnBu',
            reversescale=False,
            color=[],
            size=8,
            colorbar=dict(
                thickness=10,
                title='Node Connections',
                xanchor='left',
                titleside='right'
            ),
            line_width=1))

    # Update the text displayed on mouse over
    node_adjacencies = []
    node_text = []
    for node, adjacencies in enumerate(G.adjacency()):
        node_adjacencies.append(len(adjacencies[1]))
        node_text.append(f'{nodes[node]}: {str(len(adjacencies[1]))} connections')

    node_trace.marker.color = node_adjacencies
    node_trace.hovertext = node_text

    return node_trace, edge_trace
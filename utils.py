import random
import networkx as nx
import pickle

import plotly.offline as py
import plotly.graph_objects as go

# Traverse the graph by selecting the most weighted item
def traverse_graph(G, item, traversals, cutoff=1, random_=False):
    ''' Function that finds items in the graph 'cutoff' length away
    Args: G - the netwowrkx Graph object
          item: the start node for searching -> str
          traversals: how many results to return -> int
          cutoff - depth of neighbourhood to search -> int
          random_ - indicates whether to jump to a neighbour at random (True) or to choose the one
                    with the greatest weight (False) -> bool
    Returns: a list of connected ingredients
    '''
    items = []
    items.append(item)
    for _ in range(traversals):
        connections = nx.single_source_shortest_path_length(G, source=item, cutoff=cutoff)
        del connections[item]
        neighbours = {}
        for conn in connections:
            neighbours[conn] = G.get_edge_data(item, conn)['weight']

        weighted_neighbours = {k: v for k, v in sorted(neighbours.items(), key=lambda item: item[1], reverse=True)}

        if random_:
            new_item = random.sample(set(weighted_neighbours.keys()), 1)[0]
        else:
            new_item = list(weighted_neighbours.keys())[0]

        i = 1

        while new_item in items:
            if random_:
                new_item = random.sample(set(weighted_neighbours.keys()), 1)[0]
            else:
                new_item = list(weighted_neighbours.keys())[i]
            i += 1

            if i > 20:
                break

        item = new_item
        items.append(item)

    return items


def find_ingredient(ingredient, nodes):
    ''' Function that returns the closet match to an ingredient in the graph
    Args: ingredient: the ingredient you want to find -> str
          nodes: a list of the nodes in the graph -> list
    Returns: a list of the closest ingredients found
    '''
    ingredients = []
    for node in nodes:
        if ingredient in node:
            ingredients.append(node)

    return ingredients


def load_graph(min_edges = 3):
    ''' Function that creates the graph of the graph based on the min number of edges
    Args: min_edges: only display nodes with this or more edges -> int
    Returns: graph and pos objects
    '''
    ### Load the data up
    with open('pair_counts.pickle', 'rb') as f:
        food_df = pickle.load(f)

    # Create the graph
    d = food_df.iloc[:10000, :].set_index('products').T.to_dict('records')
    G = nx.Graph()

    for key, val in d[0].items():
        G.add_edge(key[0], key[1], weight = val)

    nodes = list(G.nodes)

    # Prune the plot so we only have items that are matched with at least min_edges others
    for node in nodes:
        try:
            if G.degree[node] < min_edges:
                G.remove_node(node)
        except:
            print(f'error with node {node}')

    nodes = list(G.nodes)
    pos = nx.spring_layout(G)

    return pos, G

def create_graph_display(G, pos):
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
        hovertext="12",
        text=nodes,
        marker=dict(
            showscale=True,
            colorscale='YlGnBu',
            reversescale=False,
            color=[],
            size=10,
            colorbar=dict(
                thickness=10,
                title='Node Connections',
                xanchor='left',
                titleside='right'
            ),
            line_width=2))

    node_adjacencies = []
    node_text = []
    for node, adjacencies in enumerate(G.adjacency()):
        node_adjacencies.append(len(adjacencies[1]))
        node_text.append(f'{nodes[node]}: {str(len(adjacencies[1]))} connections')

    node_trace.marker.color = node_adjacencies
    node_trace.hovertext = node_text

    return node_trace, edge_trace
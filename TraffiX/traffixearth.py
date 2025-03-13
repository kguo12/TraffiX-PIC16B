# This module utilizes OpenStreetMapNetworkX (OSMNX) and its stored traffic and road data in graph format.
# It converts coordinates and a radius into a directed acyclic graph that is usable by our model and simulation. 
# The main function is irl_to_traffix_model

from traffix import *
import random
import numpy as np
import osmnx as ox
import pandas as pd
import networkx as nx

def irl_to_traffix_model(coordinates, radius):
    """
    Takes in coordinates (x, y) or (long, lat) and a radius size, and returns a model able to be simulated with TraffiX
    Arguments
    coordinates - tuple for x and y coordinates
    radius - how large of an area you want to map
    The maximum number of nodes it will plot is 25. It will raise an Assertion error if the inputted area
    is too large, asking the user to reduce.
    """
    # Load in OSMNX graph
    G_raw = ox.graph.graph_from_point(coordinates, dist=radius, network_type="drive")
    
    # Graph reduction to acyclic graph for modeling purposes, remove isolated nodes, get weakly-connected graph
    while not nx.is_directed_acyclic_graph(G_raw):
        edges_to_remove = list(nx.find_cycle(G_raw, orientation="original"))
        G_raw.remove_edges_from(edges_to_remove)
    components = list(nx.weakly_connected_components(G_raw))
    largest_component = max(components, key=len)
    G = G_raw.subgraph(largest_component).copy()
    G.remove_nodes_from(list(nx.isolates(G)))

    # Check for weakly-connected, directed acyclic, size of graph is feasible
    assert nx.is_weakly_connected(G), "Invalid Area. Resulting map is not weakly connected/not present."
    assert nx.is_directed_acyclic_graph(G), "Invalid Area. Modifications did not produce a DAG. Please choose a different area."
    assert len(G.nodes) <= 25, "Please reduce the size of the requested region (lower radius, choose less dense area)."
    
    # Get positions based on node coordinates for more accurate visualization (using geo Pandas dataframes)
    nodes, edges = ox.graph_to_gdfs(G)
    nodes = nodes.reset_index()
    edges = edges.reset_index()
    # Normalize coords
    nodes['xpos'] = (nodes['x'] - nodes['x'].min()) / (nodes['x'].max() - nodes['x'].min())
    nodes['ypos'] = (nodes['y'] - nodes['y'].min()) / (nodes['y'].max() - nodes['y'].min())
    # Round edge lengths to nearest multiple of 50, nonzero (for seg_len purposes in traffix.py)
    edges['length'] = round(edges['length'] / 50, 0) * 50
    edges.loc[edges['length'] == 0, 'length'] = 50
    # Fill in lane NaN and invalid values (e.g. lists) with 1
    edges['lanes'].fillna(1, inplace=True)
    edges['lanes'] = edges['lanes'].apply(lambda x: 1 if isinstance(x, list) else x)
    edges['lanes'] = edges['lanes'].astype(int)
    
    # Instantiation of TraffiX model
    model = Map(confirmation_messages = False)
    
    for node_row in range(len(nodes)):
        name = nodes.loc[node_row, 'osmid']
        position = (nodes.loc[node_row, 'xpos'], nodes.loc[node_row, 'ypos'])
        model.add_inter(label=name, pos=position)
        
    #m.add_road(1, 2, dt=1, speed_limit=50, length=100, lanes=1, num_cars=0)
    for edge_row in range(len(edges)):
        start = edges.loc[edge_row, 'u']
        end = edges.loc[edge_row, 'v']
        speed_limit = 50
        # this is a shortcoming of the osmnx dataset. Speed limits are often not listed for road segments so we just make this assumption here.
        # really, this model makes a lot of gross assumptions, so this comparatively isn't too gross.
        length = edges.loc[edge_row, 'length']
        lanes = edges.loc[edge_row, 'lanes']
        model.add_road(start, end, dt=1, speed_limit=speed_limit, length=length, lanes=lanes, num_cars=0)
    
    print(f"""
    Uncompiled model of IRL road network at {coordinates} with radius {radius} returned.
    Please declare input nodes and initialize number of cars to sinks before compilation.
    The current summary of the graph (with sinks) and a sketch of the graph are below.
    """)
    model.get_summary()
    nx.draw(model.G, pos=model.node_positions)
    
    # Display root nodes for potential inputs the user can provide
    in_degrees = dict(model.G.in_degree(model.G.nodes))
    roots = [node for node in in_degrees if in_degrees[node] == 0]
    print(f"""
    For reference, the root nodes that can serve as potential inputs are:
    {roots}
    Initialize inputs with:
    - .declare_inflow_node(source_node (its name), initial_cars_to_sinks (dictionary, sinks are keys, num_cars are values))
    """)
    
    return model
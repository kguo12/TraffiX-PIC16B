import pandas as pd
import numpy as np
import networkx as nx
import plotly.graph_objects as go

def l1_metric(start, end):
    return (np.abs(start[0]-end[0])+np.abs(start[1]-end[1]))

def shortest_path(points, start_index, end_index):
    """
    Currently implemented with arbitrary coordinates
    Assuming l_1 metric, shortest total path length given start and end coordinates 
    Honestly at the moment just a traveling salesman problem but whatever
    """
    G = nx.Graph()
    for i, (x, y) in enumerate(points):
        G.add_node(i, pos=(x, y))
    for i in range(len(points)):
        for j in range(i+1, len(points)):
            G.add_edge(i, j, weight = l1_metric(points[1], points[j]))
    #tsp_path = nx.algorithms.approximation.traveling_salesman.traveling_salesman_problem(G, cycle=False)
    simple_path = list(nx.shortest_simple_paths(G, start_index, end_index))

    return simple_path
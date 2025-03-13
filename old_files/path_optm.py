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
            G.add_edge(i, j, weight = l1_metric(points[i], points[j]))
    tsp_path = nx.algorithms.approximation.traveling_salesman.traveling_salesman_problem(G, cycle=False)
    #simple_path = list(nx.shortest_simple_paths(G, start_index, end_index))

    path_coords = [points[i] for i in tsp_path]

    # Create a Plotly figure
    fig = go.Figure()
    
    # Add scatter plot for the points
    fig.add_trace(go.Scatter(
        x=points[:, 0], y=points[:, 1],
        mode='markers+text',
        text=[f"Point {i}" for i in range(len(points))],
        textposition="top center",
        marker=dict(size=10, color='lightblue'),
        name="Points"
    ))
    
    # Add lines for the TSP path
    path_x = [points[i][0] for i in tsp_path]
    path_y = [points[i][1] for i in tsp_path]
    fig.add_trace(go.Scatter(
        x=path_x, y=path_y,
        mode='lines+markers',
        line=dict(color='red', width=2),
        name="Shortest Path"
    ))
    
    # Highlight start and end points
    fig.add_trace(go.Scatter(
        x=[points[start_index][0]], y=[points[start_index][1]],
        mode='markers',
        marker=dict(size=15, color='green'),
        name="Start Point"
    ))
    fig.add_trace(go.Scatter(
        x=[points[end_index][0]], y=[points[end_index][1]],
        mode='markers',
        marker=dict(size=15, color='blue'),
        name="End Point"
    ))
    
    # Update layout for better visualization
    fig.update_layout(
        title="Shortest Path",
        xaxis_title="X Coordinate",
        yaxis_title="Y Coordinate",
        showlegend=True
    )
    
    # Show the plot
    fig.show()

    #return tsp_path
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.animation import FuncAnimation
from IPython.display import HTML
import networkx as nx
import numpy as np
from tqdm import tqdm


def simulate(m, frames=150):
    """
    Performs a simulation for a given model (m) across a number of frames.
    Returns: HTML matplotlib animation of traffic simulation, coloring roads by num_cars.
    """
    progress_bar = tqdm(total=frames, position=0, leave=True)
    m = m # instatiate the model
    
    # Define update function using model
    
    norm = plt.Normalize(0, 1)  # Normalize to [0,25]
    node_colors = [cm.Reds(norm(0)) for _ in range(len(m.G.nodes))]
    def update(frame):
        ax.clear()  # Clear previous frame, update progress bar
        progress_bar.update(1)

        # Update traffic by one time step
        m.update_time()

        # Update edge_colors
        num_cars = nx.get_edge_attributes(m.G, 'num_cars')
        # Convert weights to a list and normalize them for color mapping
        num_cars_values = list(num_cars.values())
        norm = plt.Normalize(0, 10)  # Normalize to [0,25]
        edge_colors = [cm.Reds(norm(num_cars[edge])) for edge in m.G.edges]

        # Redraw graph
        nx.draw(m.G, m.node_positions, ax=ax, with_labels=False, 
                node_color=node_colors, node_size=0, 
                edge_color=edge_colors, width=7)

        # Create labels for terminations, num_cars
        shift_down_pos = {node: (x, y - 0.05) for node, (x, y) in m.node_positions.items()}

        terminations = {sink_node: "Terms:\n" + str(round(m.G.nodes[sink_node]["terminations"],2)) for sink_node in m.sinks}
        nx.draw_networkx_labels(m.G, shift_down_pos, ax=ax, labels=terminations, font_size=15, font_color="black")

        road_num_cars = {edge: "" + str(round(m.G[edge[0]][edge[1]]["num_cars"],2)) for edge in m.G.edges}
        #nx.draw_networkx_edge_labels(m.G, shift_down_pos, ax=ax, edge_labels=road_num_cars, font_size=15, font_color="black")
    
    # Run animation
    
    fig, ax = plt.subplots(figsize=(20,10))
    fig.set_facecolor("0.3")
    ani = FuncAnimation(fig, update, frames=frames, interval=200)
    plt.close()
    return HTML(ani.to_jshtml())
import networkx as nx
import osmnx as ox
from plotly import express as px

def optimal_walk_route(start, end):
    '''
    FURTHER TO DOS
    1) start and end work right now as tuples of coordinates (lat, long), potentially in future
    user could provide a name of a landmark --> google maps API --> get coordinates --> input here
    2) Also, the interactive map could be actually "interactive", allow user to click on the map,
    store inputs into coordinates, then plot out optimal_route
    3) the weights right now are only the lengths, should include data on busyness/high traffic walking
    routes to change up the weights used by Shortest path algo
    '''
    
    # Make graph of UCLA walking routes
    G = ox.graph.graph_from_point((34.07, -118.445), dist=750, network_type="walk")
    
    # Get the start and end nodes
    start_node = ox.distance.nearest_nodes(G, start[1], start[0])
    end_node = ox.distance.nearest_nodes(G, end[1], end[0])
    print("Start at: Latitude: ", G.nodes[start_node]['y'], "Longitude: ", G.nodes[start_node]['x'])
    print("End at: Latitude: ", G.nodes[end_node]['y'], "Longitude: ", G.nodes[end_node]['x'])
    
    # Compute the shortest path, get the coordinates along the path
    shortest_path = nx.shortest_path(G, source=start_node, target=end_node, weight="length")
    path_lats = [G.nodes[node]['y'] for node in shortest_path]
    path_longs = [G.nodes[node]['x'] for node in shortest_path]
    
    # Plot out plotly map of the shortest route
    fig = px.scatter_mapbox(lat = path_lats,
                        lon = path_longs, 
                        zoom = 15,
                        height = 300,
                        mapbox_style="open-street-map")

    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.show()
    
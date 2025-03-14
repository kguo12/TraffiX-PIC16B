import networkx as nx
import numpy as np
import random
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.animation import FuncAnimation
from IPython.display import HTML
import networkx as nx
from tqdm import tqdm

def weighting(data):
    """
    Simple weighting by proportion of total.
    """
    return data / data.sum()

def inv_weighting(data):
    """
    Inverse weighting, giving higher weight to lower values.
    """
    return (1/data) / (1/data).sum()

def add_dicts(dict1, dict2):
    """
    Adding dictionary values by key.
    """
    result = dict1.copy()
    for key, value in dict2.items():
        result[key] = result.get(key, 0) + value
    return result

class Map:
    """
    Road network class.
    """
    # Initialization methods
    
    def __init__(self, capacity_per_length_per_lane = .5, 
                 green_lights_per_time = 3, 
                 ideal_send_per_lane_per_green = 10,
                 confirmation_messages = True, 
                 seg_len = 20, 
                 dt=1, 
                 flow_constant = 5): # should we add flow hesitancy/intertia
        """
        Parameters:
        capacity_per_length_per_lane: specifies how capacity for each road segment should be calculated. This constant is multiplied by lanes and length.
        green_lights_per_time: OUTDATED, used to determine the number of green lights for each time step.
        ideal_send_per_lane_per_green: this controls the maximum number of cars a given lane for a road will send into an intersection. It is reduced
        by speed_factor (see below).
        confirmation_messages: default to True, allows messages when calling add_road, add_inter, simulation_check_compile, etc.
        seg_len: specifies the length each road initialization should be split up by into segments.
        
        G: the graph.
        node_positions: the positions of the nodes when visualizing with matplotlib.
        num_lanes: the total number of lanes in the network.
        total_length_of_road: the total length of road used in the network.
        inputs: the nodes declared as inputs with .declare_inflow_node.
        cars_to_sinks_dict: the initial traffic count in the simulation, and the destination sink points for all cars.
        """
        self.G = nx.DiGraph()
        self.node_positions = {}
        self.capacityPLPL = capacity_per_length_per_lane
        self.idealSPLPG = ideal_send_per_lane_per_green
        self.GLPT = green_lights_per_time
        self.seg_len = seg_len
        self.dt = dt
        self.flow_constant = flow_constant
        
        self.confirmation = confirmation_messages
        if self.confirmation:
            print("""
            Road network initialized. Methods: \n
            - .add_inter(label, pos)
            - .add_road(start, end, speed_limit, lanes, num_cars = 0)
            - .simulation_status_check()
            """)
        
        self.num_lanes = 0
        self.total_length_of_road = 0
        self.inputs = []
        self.input_temp_nodes = []
        self.cars_to_sinks_dict = {}
        
        
    def add_inter(self, label, pos):
        """
        Adds an intersection and assigns it a label and a position (tuple)
        """
        # label can be int or str
        self.G.add_node(label)
        self.node_positions[label] = pos
        if self.confirmation:
            print(f"Intersection {label} added.")
        
    def add_road(self, start, end, speed_limit, length, lanes, num_cars = 0):
        """
        Adds a road from node labels.
        """
        try:
            start_pos = self.node_positions[start]
            end_pos = self.node_positions[end]
            pos = start_pos
            direction = np.subtract(end_pos, start_pos)
            # we round the road length according to the seg_len
            num_segs = round(length / self.seg_len)

            # intermediate intersection positions are purely for visualization purposes
            last_inter = start
            for i in range(num_segs-1):
                pos += direction/num_segs
                next_inter = "(" + str(start) + "," + str(end) + ")" + " S" + str(i) # (u,v) S0
                self.add_inter(next_inter, tuple(pos)) 
                
                self.G.add_edge(last_inter, next_inter, capacity=self.capacityPLPL*self.seg_len*lanes, speed_limit=speed_limit, length=self.seg_len, lanes=lanes, num_cars=num_cars)
                last_inter = next_inter
                
            
            self.G.add_edge(last_inter, end, capacity=self.capacityPLPL*self.seg_len*lanes, speed_limit=speed_limit, length=self.seg_len, lanes=lanes, num_cars=num_cars)
            self.total_length_of_road += lanes*length
            self.num_lanes += lanes

            if self.confirmation:
                print(f"Road with {lanes} lanes between {start} and {end} added.")
            
        except:
            print("Nodes do not exist.")
            
        
    def get_summary(self):
        """
        Does not modify network. Returns summary statistics of the road network before or after compilation.
        """
        out_degrees = dict(self.G.out_degree(self.G.nodes))
        sinks = [node for node in out_degrees if out_degrees[node] == 0]
        print(f"""
        Resources Used:
        - Total length of road used: {self.total_length_of_road} units
        - Total number of lanes: {self.num_lanes}
        Key Nodes:
        - Inputs: {self.inputs}
        - Sinks: {sinks}
        - Sink destination amounts/Total traffic: {self.cars_to_sinks_dict}
        """)
            
    # Traffic initialization
    
    def declare_inflow_node(self, source_node, initial_cars_to_sinks):
        """
        Takes an input node and assigns it some initial number of cars and their sink destinations.
        """
        mod_initial_cars_to_sinks = {(source_node, sink): initial_cars_to_sinks[sink] for sink in initial_cars_to_sinks}
        self.cars_to_sinks_dict = add_dicts(self.cars_to_sinks_dict, mod_initial_cars_to_sinks)
        initial_cars = 0
        for key in initial_cars_to_sinks:
            initial_cars += initial_cars_to_sinks[key]
        
        self.inputs.append(source_node)
        input_name = "_i" + str(len(self.inputs))
        self.G.add_node(input_name)
        self.input_temp_nodes.append(input_name)
        self.node_positions[input_name] = (self.node_positions[source_node][0] - 0.1, self.node_positions[source_node][1])
        self.add_road_segment(input_name, source_node, speed_limit=50, length=100, lanes=1, num_cars=initial_cars)
        self.num_lanes -= 1
        self.total_length_of_road -= 100
        if self.confirmation:
            print("Inflow node declared.")

    def add_road_segment(self, start, end, speed_limit, length, lanes, num_cars = 0):
        try:
            self.G.add_edge(start, end, capacity=self.capacityPLPL*length*lanes, speed_limit=speed_limit, length=length, lanes=lanes, num_cars=num_cars)
            if self.confirmation:
                print(f"Road with {lanes} lanes between {start} and {end} added.")
            self.num_lanes += lanes
            self.total_length_of_road += lanes*length
        except:
            print("Nodes do not exist.")
    
    # Check and Compilation for simulation
    
    def simulation_check_compile(self):
        """
        Checks if the road network is suitable for simulation
        - Directed and acyclic?
        - Calculate intersection turn probabilities
        - instantiate self.sinks
        Returns summary messages and a sketch of the graph.
        """
        # Check for acyclic
        assert nx.is_directed_acyclic_graph(self.G), "Constructed road network is not acyclic. Please try again."
        
        # Store sink points, give terminations attributes
        out_degrees = dict(self.G.out_degree(self.G.nodes))
        self.sinks = [node for node in out_degrees if out_degrees[node] == 0]
        for node in self.sinks:
            self.G.nodes[node]['terminations'] = 0
        
        # Calculate and endow intersection turn probabilities
        edge_counts = {}
            # Update total cars travelled for each edge
        for source_node, sink in self.cars_to_sinks_dict.keys():
            paths = list(nx.all_simple_edge_paths(self.G, source_node, sink))
            # Calculate path weights from source to sink
            path_lengths = np.zeros(len(paths))
            for index, path in enumerate(paths):
                total_length = 0
                for edge in path:
                    total_length += self.G[edge[0]][edge[1]]['length']
                path_lengths[index] = total_length
            path_weights = inv_weighting(path_lengths)
            
            # Calculate num of cars on path
            route_num_cars = self.cars_to_sinks_dict[(source_node, sink)]
            path_num_cars = path_weights * route_num_cars
            
            # Add total cars travelled for each edge
            for index, path in enumerate(paths):
                for edge in path:
                    try:
                        edge_counts[edge] += path_num_cars[index]
                    except KeyError:
                        edge_counts[edge] = path_num_cars[index]
            
            # Endow intersections with probabilities
        for node in self.G.nodes:
            if node in self.input_temp_nodes:
                continue
            out_edges = list(self.G.out_edges(node))
            out_edges_cars = []
            for edge in out_edges:
                out_edges_cars.append(edge_counts[edge])
            out_edges_cars = np.array(out_edges_cars)
            out_edges_weights = weighting(out_edges_cars)
            for i, edge in enumerate(out_edges):
                self.G.nodes[node][edge] = out_edges_weights[i]
            
        if self.confirmation:
            print(f"""
            Road network satisfactory and ready for simulation. Summary:
            - Input Nodes: {self.inputs}
            - Sinks: {self.sinks}
            - Number of lanes used: {self.num_lanes}
            - Total length of road used: {self.total_length_of_road}
            - Intersection turn probabilities calculated using shortest-path simple weighting. 
              Access or manually edit through map.G.nodes attributes.
            Network sketch:
            """)
            nx.draw(self.G, self.node_positions)
        
    # Simulation, time-step update for road network
    
    def update_time(self):
        """
        Moves the simulation forward one time-step. This involves
        1. Randomizing the order of the green lights
        2. Calculating speed_factors and num_cars to send for each edge
        3. Updating num_cars for each edge after each send into intersection
        """
        # loop through each edge non-simultaneously for each time step ("green light-red light")
        # green_lights = [random.randint(0, len(self.G.edges)-1) for _ in range(self.GLPT)]
        green_lights = [i for i in range(len(self.G.edges))]
        random.shuffle(green_lights)
        for green_light in green_lights:
            edge = list(self.G.edges)[green_light]
            inter = edge[1]
            out_edges = list(self.G.out_edges(inter))

            # handle case leading to sink
            """
            if len(out_edges) == 0:
                speed_factor = max(self.G[edge[0]][edge[1]]['capacity'] - self.G[edge[0]][edge[1]]['num_cars'],0) / self.G[edge[0]][edge[1]]['capacity'] + 0.2
                #print(speed_factor)
                # send calculated amount, or remaining cars in road
                to_send_num = min(self.idealSPLPG * self.G[edge[0]][edge[1]]['lanes'] * speed_factor, self.G[edge[0]][edge[1]]['num_cars'])
                if to_send_num == 0:
                    pass
                self.G.nodes[inter]['terminations'] += to_send_num
                self.G[edge[0]][edge[1]]['num_cars'] -= to_send_num
                pass
            """

            to_send = {out_edge: self.G.nodes[inter][out_edge] for out_edge in out_edges}
            # between r>0 and 1, note that r attains smaller positive value iff road capacity is large (i.e. a huge jammed multi-lane highway vs. local road)

            # the max possible that can be sent without overflow
            fluxes = [(self.G[out_edge[0]][out_edge[1]]['capacity'] - self.G[out_edge[0]][out_edge[1]]['num_cars'])/to_send[out_edge] for out_edge in out_edges]
            fluxes = np.array(fluxes)
            try:
                out_flux_cap = float(np.min(fluxes))
                ### Is this how the system works 
                
                # take into account speed
                max_out_flux = min(out_flux_cap,  self.G[edge[0]][edge[1]]['num_cars'] * self.dt * self.flow_constant / self.G[edge[0]][edge[1]]['length']) 
                # take into account lanes????
                to_send_num = min(max_out_flux, self.G[edge[0]][edge[1]]['num_cars'])



                #speed_factor = max(self.G[edge[0]][edge[1]]['capacity'] - self.G[edge[0]][edge[1]]['num_cars'],0) / self.G[edge[0]][edge[1]]['capacity'] + 0.2 # old version
                # send calculated amount, or remaining cars in road
                #to_send_num = min(self.idealSPLPG * self.G[edge[0]][edge[1]]['lanes'] * speed_factor, self.G[edge[0]][edge[1]]['num_cars']) # old version
                
            except ValueError: # if it is a sink, min will be empty
                speed_factor = max(self.G[edge[0]][edge[1]]['capacity'] - self.G[edge[0]][edge[1]]['num_cars'],0) / self.G[edge[0]][edge[1]]['capacity'] + 0.2
                #print(speed_factor)
                # send calculated amount, or remaining cars in road
                to_send_num = min(self.idealSPLPG * self.G[edge[0]][edge[1]]['lanes'] * speed_factor, self.G[edge[0]][edge[1]]['num_cars'])
                if to_send_num == 0:
                    pass
                self.G.nodes[inter]['terminations'] += to_send_num
                self.G[edge[0]][edge[1]]['num_cars'] -= to_send_num


            # Send cars, check for capacity, retain if overflow, remove cars from edge

            for out_edge in to_send:
                num_send = to_send[out_edge] * to_send_num
                self.G[edge[0]][edge[1]]['num_cars'] -= num_send
                self.G[out_edge[0]][out_edge[1]]['num_cars'] += num_send
            """
            for out_edge in to_send:
                num_send = to_send[out_edge] * to_send_num
                would_be_capacity = num_send + self.G[out_edge[0]][out_edge[1]]['num_cars']
                if would_be_capacity > self.G[out_edge[0]][out_edge[1]]['capacity']:
                    actual_sent = self.G[out_edge[0]][out_edge[1]]['capacity'] - self.G[out_edge[0]][out_edge[1]]['num_cars']
                    self.G[edge[0]][edge[1]]['num_cars'] -= actual_sent
                    self.G[out_edge[0]][out_edge[1]]['num_cars'] = self.G[out_edge[0]][out_edge[1]]['capacity']
                else:
                    self.G[edge[0]][edge[1]]['num_cars'] -= num_send
                    self.G[out_edge[0]][out_edge[1]]['num_cars'] += num_send"
            """
            # I don't think I need this




                    
                
            
            
            
        

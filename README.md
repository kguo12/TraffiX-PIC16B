# TraffiX (1.0)
## By [Mario Truong](https://mariotruong27.github.io/16blog/), [Henry Tang](https://tanghenry63.github.io/pic16b/), and [Kenny Guo](https://kguo12.github.io/kennyguowebpage/)

*Final Project for UCLA PIC 16B (25W, S. Burnett).*

This is TraffiX, a Python package for building and simulating artificial or real-life traffic networks utilizing NetworkX and OSMNX capabilities. You may download the **TraffiX Package** above. 

#### Sections
1. [Introduction and Overview](#intro)
2. [Documentation/User Reference](#documentation)

## Introduction<a name="intro"></a>

Welcome to this introduction on **TraffiX (version 1.0)**, a Python package for building and simulating artificial or IRL traffic networks utilizing NetworkX and OSMNX capabilities developed by [Mario Truong](https://mariotruong27.github.io/16blog/), [Henry Tang](https://tanghenry63.github.io/pic16b/), and [Kenny Guo](https://kguo12.github.io/kennyguowebpage/). As UCLA students living in the sprawling city of Los Angeles, we are all too familiar with the sight of piled up highways and the dread of seemingly everlasting commutes. Motivated by this issue and with our background as applied math students, we decided for our Python project to create a model for simulating cars and traffic flowing through a road network, dubbed TraffiX (*[/ˈtræfɪk/]*). You can read more about the project, the background and setup of the model, and learn how to build and import your own TraffiX models at the blog post [here](https://kguo12.github.io/kennyguowebpage/posts/traffix%20project/).

## Documentation and User Reference<a name="documentation"></a>

#### **Class**: `Map`

Represents a road network TraffiX model using NetworkX. Provides methods to construct a directed graph with roads and intersections, declare inflow nodes, check and compilation of model for simulation, and run time-step updates for traffic movement.

`__init__`
Initializes an empty directed graph and key parameters for TraffiX model.

Arguments:
- `capacity_per_length_per_lane` (float, default=0.5) – Defines road segment capacity per unit length per lane.
- `green_lights_per_time` (int, default=3) – Number of roads that get green lights per time step.
- `ideal_send_per_lane_per_green` (int, default=10) – Ideal number of cars sent per lane per green light cycle.
- `confirmation_messages` (bool, default=True) – Enables or disables confirmation print messages.

Returns: None

`add_inter(label, pos)`
Adds an intersection node to the graph with a given position.

Arguments:
- `label` (str or int) – The intersection's unique identifier.
- `pos` (tuple of float) – The (x, y) coordinates of the intersection.

Returns: None


`add_road(start, end, dt, speed_limit, length, lanes, num_cars=0)`
Adds a segmented road between two intersections.

Arguments:
- `start` (str or int) – The starting intersection.
- `end` (str or int) – The ending intersection.
- `dt` – to be implemented
- `speed_limit` – to be implemented
- `length` (float) – Length of the road segment.
- `lanes` (int) – Number of lanes on the road.
- `num_cars` (int, default=0) – Initial number of cars on the road.

Returns: None


`get_summary()`
Prints a summary of the road network, including resource metrics such as total road length, number of lanes, input nodes, sink nodes, and traffic inputs-sinks distributions.

Arguments: None

Returns: None

`declare_inflow_node(source_node, initial_cars_to_sinks)`
Declares an inflow node and adds cars entering the system via dictionary.

Arguments:

- source_node (str or int) – The input node where cars enter the system.
- initial_cars_to_sinks (dict) – Mapping of sink nodes to the number of cars sent toward them.

Returns: None

`add_road_segment(start, end, dt, speed_limit, length, lanes, num_cars=0)`
Adds a road segment between two nodes without intermediate intersections.

Arguments:
- Same as add_road().

Returns: None

`simulation_check_compile()`
Ensures the road network is acyclic before simulation, initializes sinks and terminations attributes, calculates and assigns intersection turn proportions, and displays a network visualization and summary (if self.confirmation == True).

Arguments: None

Returns: None

`update_time()`
Simulates a single time step of traffic movement.

Arguments: None

Returns: None

#### **Function**: `simulate`
The `simulate` function animates a TraffiX model traffic simulation over a specified number of frames, visualizing the traffic flow through a road network.

`simulate(m, frames=150)`

Arguments:
- `m` (Map object): An instance of a TraffiX model, containing a networkx graph (m.G), node positions (m.node_positions), and methods for updating the simulation (m.update_time()).
- `frames` (int, default=150): Number of time steps to run the simulation.

Returns:
- HTML FuncAnimation object containing a matplotlib animation of the traffic simulation.

#### **Function**: `irl_to_traffix_model`
The `irl_to_traffix_model` function converts real-world NetworkX road networks from OpenStreetMap into a directed acyclic graph (DAG) compatible with TraffiX modeling and simulation.

`irl_to_traffix_model(coordinates, radius)`

Arguments:

- coordinates (tuple): Latitude and longitude of the location to map.
- radius (float): The radius (in meters) around the given coordinates to extract road data.

Returns:

- A TraffiX model `Map` object of the road network in a format that can be simulated.

#### **Function**: `template_2input_1sink`
Returns: 
- A simple road network model (Map object) with two input sources and one sink.
#### **Function**: `template_bridge(num_bridge_lanes=1, speed_limit=50)`

Arguments:
- num_bridge_lanes (int): Number of lanes on the bridge (must be ≥ 1).
- speed_limit: to be implemented

Returns: 
- A bridge traffic model (Map object) with variable lane capacity.



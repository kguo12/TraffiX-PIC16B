#### Updated version of simple_sim (Updated: 3/6/2025)


Features
- input road with starting number of cars $n_0$
- sink points (ralphs), each car $\in [n_0]$ is pursuing one of these points
- intersection probabilities are calculated as follows: for all of the routes from input to sink point for a given car, the car is equally likely to take any of them. Sum up the total routes across the network, and normalize accordingly to get the probabilities. 
- directed, acyclic graph (cars are assumed to flow from input to sink only)
- roads have max-capacities. 
For a given time *episode*,
- (traffic lights) each road will be updated ("green light") one by one, randomly. At any given "green light", $n_0$ (the current amount of cars on the round) times $cv$ (some constant times current road speed) will be the maximum number sent into the intersection, and split up according to p's. If the roads are at max capacity, this may be lower.
- The episode ends when all intersections have been updated once.

We evaluate a road network by the number of episodes needed for all initial cars to reach the sink points. This can be influenced by certain input parameters, the most important of which is **the structure of the road network**. We additionally will run experiments with constraints, including
- limiting the number of possible roads
- limiting the carrying capacity of each road
and varying other parameters, such as:
- number of initial cars
- sink point destinations for each car
import random

class Map:
    def __init__(self, intersections, roads):
        self.intersections = intersections
        self.roads = roads

    def update(self):
        for road in self.roads:
            road.update()

class Intersection:
    def __init__(self, roads=[]):
        self.roads = roads # in ccw order ?
        self.terminations = 0

        self.get_out_roads()

    def add_road(self, road):
        self.roads.append(road)
        self.get_out_roads()

    def get_out_roads(self):
        self.out_roads = []
        for road in self.roads:
            if road.get_start() == self:
                self.out_roads.append(road)

    def route(self, in_road, num_cars, direction=None):
        if direction == None: # if direction is not None
            
            if in_road.num_cars >= num_cars:
                in_road.remove_cars(num_cars)
            else:
                in_road.num_cars = 0


            if len(self.out_roads) != 0:
                choice = random.choice(self.out_roads)
                choice.add_cars(num_cars)# choose random road
            else:
                self.terminations += num_cars
                
            # else cars just disappear




class Road:
    def __init__(self, dt, start, end, num_cars, speed_limit, length, lanes, name):
        self.dt = dt # size of time step
        self.start = start # starting intersection
        self.end = end # ending intersection
        self.num_cars = num_cars # number of cars
        self.speed_limit = speed_limit
        self.length = length # length of road
        self.lanes = lanes # number of lanes
        self.name = name
        
        self.connect()
        self.speed = 0
        self.update_speed()

    def connect(self):
        self.start.add_road(self)
        self.end.add_road(self)

    def update_speed(self):
        if self.num_cars > 0:
            self.speed =  self.speed_limit / self.num_cars
        else:
            self.speed = self.speed_limit
    
    def get_start(self):
        return self.start
    
    def update(self):
        self.end.route(in_road = self, num_cars = (self.num_cars * self.speed * self.dt)/self.length) 

        bar = ""
        for i in range(int(self.num_cars)):
            bar += "#"

        #print(self.name, bar)
        # send number of cars into intersection based on uniform density of cars

    def add_cars(self, num_cars):
        self.num_cars += num_cars
    def remove_cars(self, num_cars):
        self.num_cars -= num_cars
from collections import deque
import uuid
import sys
import json

from django import conf
class Network():
    """
    Global Network Object. Creates a graph from a supplied json file
    Allows the addition of new road/intersections (Edge/Vertex) and car objects on demand.
    """
    def __init__(self, name) -> None:
        print("USING: " + name + ".json as configuration file")
        config = None
        config_file = None
        try:
            config_file = open(name + '.json')
        except:
            raise Exception("Config Not Found!")
        try:
            config = json.load(config_file)
            config_file.close()
        except:
            raise Exception("Malformed Config")
        for edge in config["edges"]:
            print (edge)
    def tick(self) -> None:
        pass
class Intersection():
    def __init__(self) -> None:
        pass
    pass
class Road():
    """
    Create a one directional Road (Graph Edge)
    Road can have multiple lanes. Each lane has the same fixed capacity
    """
    lanes = []
    def __init__(self, lanes=1, lane_capacity=1) -> None:
        for lane in range(lanes):
            self.lanes.append(deque([None] * lane_capacity))
        self.id = "EDGE-" + str(uuid.uuid4())
        pass
    def add_car():
        # Check if we have a lane
        # Check if we have capacity -> Technically, we might need to have a NULL needed.
        pass

class Car():
    """
    Create a car object.
    A car object fills up one (or more) slots of a lane capacity
    """
    def __init__(self, occupancy=1) -> None:
        self.occupancy = occupancy
        self.id = "CAR-" + str(uuid.uuid4()) 
        return self.id

if __name__ == "__main__":
    NETWORK = Network(name = sys.argv[1])
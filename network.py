from collections import deque
import uuid
class Network():
    """
    Global Network Object. Creates a graph from a supplied json file
    Allows the addition of new road/intersections (Edge/Vertex) and car objects on demand.
    """
    def __init__(self) -> None:
        pass
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
    for i in range(10):
        r = Road()
        print(r.id)
import json
from collections import defaultdict
from ossaudiodev import control_names
import queue
import random
class Network():
    """
    Global Network Object. Creates a graph from a supplied json file
    Allows the addition of new road/intersections (Edge/Vertex) and car objects on demand.
    """
    def __init__(self, name) -> None:
        self.edges = defaultdict(lambda: None)
        self.nodes = defaultdict(lambda: None)
        self.cars = defaultdict(lambda: None)
        print("USING: " + name + ".json as configuration file")
        config = None
        config_file = None
        try:
            config_file = open('./configs/' + name + '.json')
            # TODO: Fully qualified name of the file we are loading. Not relative paths.
        except:
            raise Exception("Config Not Found!")
        try:
            config = json.load(config_file)
            config_file.close()
        except:
            raise Exception("Malformed Config")

        node_count = 0
        edge_count = 0
        for node in config["nodes"]:
            new_node = Node(node["id"])
            self.nodes[new_node.get_ID()] = new_node
        
        for edge in config["edges"]:
            # Make sure the edges start and end node exist
            if self.nodes[edge["from"]]:
                if self.nodes[edge["to"]]:
                    new_edge = Edge(edge["from"], edge["to"], edge["capacity"])
                    from_node = self.nodes[edge["from"]]
                    from_node.add_outbound(new_edge)
                    to_node = self.nodes[edge["to"]]
                    to_node.add_inbound(new_edge)
                    self.edges[new_edge.get_ID()] = new_edge
                else:
                    raise Exception("This Edge does not have a known destination node")
            else:
                raise Exception("This Edge does not have a known origin node")
        print("Network Created")
        # Build Each Node
        # Build Each Edge
class Node():
    def __init__(self, id):
        self.inbound_edges_id_to_edge = defaultdict(lambda: None)
        self.outbound_edges_id_to_edge = defaultdict(lambda: None)
        self.id = id
    def get_ID(self):
        return self.id
    def add_inbound(self, edge):
        self.inbound_edges_id_to_edge[edge.get_ID()] = edge
    def add_outbound(self, edge):
        self.outbound_edges_id_to_edge[edge.get_ID()] = edge
    def tick(self):
        order = self.inbound_edges_id_to_edge.keys()
        random.shuffle(order)
        for edge_id in order:
            edge = self.inbound_edges_id_to_edge[edge_id]
            if not edge.is_active():
                continue
            if not edge.has_car_waiting_to_leave():
                continue
            car = edge.pop_car_waiting_to_leave()
            # REMEMBER if you can't place the car, you must return it to the edge
            

class Edge():
    def __init__(self, from_node, to_node, capacity=2):
        self.id = id
        self.from_node = from_node
        self.to_node = to_node
        self.queue = [None] * capacity
        self.incoming_car = None
        self.activated = True
    def activate(self):
        self.activated = True
    def deactivate(self):
        self.activated = True
    def is_actve(self):
        return self.activated
    def get_to_node(self):
        return self.to_node
    def get_from_node(self):
        return self.from_node
    def __len__(self):
        return len(self.queue)
    def get_ID(self):
        return self.id
    def has_space_for_new_car(self):
        return self.queue[0] == None and self.incoming_car == None
    def add_new_car(self, car):
        self.incoming_car = car
    def has_car_waiting_to_leave(self):
        return self.queue[-1] != None
    def pop_car_waiting_leave(self):
        car = self.queue[-1]
        self.queue[-1] = None
        return car
    def return_car_to_head(self,car):
        self.place_car_at_point(car, len(self)-1, force=True)
    def place_car_at_point(self, location, car, force=False):
        if location > len(self):
            return False
        if self.queue[location] != None:
            if force:
                self.queue[location] = car
            else:
                return False
        return True

    def tick(self):
        # Find first instance of a None from the reverse.
        located_index = None
        for i in range(len(self)-1, -1, -1):
            if self.queue[i] == None:
                located_index = len(self) - i - 1
                break
        if located_index != None:
            # We have found the None
            # Everything before this point should be shifted
            unshift = self.queue[located_index+1::]
            shift = self.queue[0:located_index]
            incoming = [self.incoming_car]
            self.queue = incoming + shift + unshift
        else:
            # Well, we don't have any space it seems.
            pass
        # TODO: Check if a car has moved into it's required position!
        for car in self.queue:
            pass
class Car():
    pass
import json
from collections import defaultdict
import random
import re
class Network():
    """
    Global Network Object. Creates a graph from a supplied json file
    Allows the addition of new road/intersections (Edge/Vertex) and car objects on demand.
    """
    def __init__(self, name) -> None:
        self.edges = defaultdict(lambda: None)
        self.nodes = defaultdict(lambda: None)
        self.cars = defaultdict(lambda: None)
        self.tick_count = 0
        self.completed_count = 0
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
                    new_edge = Edge(edge["id"], edge["from"], edge["to"], edge["capacity"])
                    from_node = self.nodes[edge["from"]]
                    from_node.add_outbound(new_edge)
                    to_node = self.nodes[edge["to"]]
                    to_node.add_inbound(new_edge)
                    self.edges[new_edge.get_ID()] = new_edge
                else:
                    raise Exception("This Edge does not have a known destination node")
            else:
                raise Exception("This Edge does not have a known origin node")
        for car in config["cars"]:
            car = Car(car["id"], car["start_edge"], car["start_position"], car["end_edge"], car["end_position"], car["path"])
            car.generate_path()
            start_edge = self.edges[car.current_edge]
            print(start_edge)
            start_edge.place_car_at_point(car.current_position, car,force=True) # TODO, check if possible, otherwise do something
            print (start_edge.queue)
            self.cars[car.id] = car
        print("Network Created")

    
    def tick(self):
        self.tick_count +=1
        order = list(self.nodes.keys())
        random.shuffle(order)
        for node_id in order:
            node = self.nodes[node_id]
            self.completed_count += (node.tick())
        #TODO: Output Snapshot 
    def create_snapshot(self):
        raise Exception("Not implemented")
        #TODO: Create Snapshot
        # 1. Get State of system
        # 2. Save as output json
    def get_system_overview(self):
        return { "Tick" : self.tick_count, "Completed Count" : self.completed_count}
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
        completed_count = 0
        order = list(self.inbound_edges_id_to_edge.keys())
        random.shuffle(order)
        for edge_id in order:
            edge = self.inbound_edges_id_to_edge[edge_id]
            if not edge.is_active():
                continue
            if edge.has_car_waiting_to_leave():
                car = edge.pop_car_waiting_to_leave()
                # REMEMBER if you can't place the car, you must return it to the edge
                # Process
                # 1. Figure out car's next target edge
                # 2. Figure out if the target edge is valid, enabled, and has capacity
                # 3. If so, move the car to the target edge.
                #    If not, return the car to the edge it came from.
                target_edge_id = car.get_next_edge()
                target_edge = self.outbound_edges_id_to_edge[target_edge_id]
                if target_edge == None:
                    raise Exception("Invalid Edge Selected! PANIC!")
                if target_edge.is_active() and target_edge.has_space_for_new_car():
                    target_edge.add_new_car(car)
                else:
                    edge.return_car_to_head(car)
                # TODO: Think long and hard about tick order
            completed_count += edge.tick()
        return completed_count



            

class Edge():
    def __init__(self, edge_id, from_node, to_node, capacity=2):
        self.id = edge_id
        self.from_node = from_node
        self.to_node = to_node
        self.queue = [None] * capacity
        self.incoming_car = None
        self.activated = True
    def activate(self):
        self.activated = True
    def deactivate(self):
        self.activated = True
    def is_active(self):
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
    def pop_car_waiting_to_leave(self):
        car = self.queue[-1]
        self.queue[-1] = None
        return car
    def return_car_to_head(self,car):
        self.place_car_at_point(len(self.queue)-1, car, force=True)
    def place_car_at_point(self, location, car, force=False):
        print(location)
        if location > len(self.queue):
            return False
        elif self.queue[location] != None:
            if force:
                self.queue[location] = car
            else:
                return False
        else:
            self.queue[location] = car
        return True

    def tick(self):
        completed_count = 0
        print(self.id, "\t TICK: \t", self.queue)
        # Find first instance of a None from the reverse.
        located_index = None
        for i in range(len(self.queue)-1, -1, -1):
            if self.queue[i] == None:
                located_index = i
                break
        if located_index != None:
            # We have found the None
            # Everything before this point should be shifted
            unshift = self.queue[located_index+1::]
            shift = self.queue[0:located_index]
            incoming = [self.incoming_car]
            self.incoming_car = None
            self.queue = incoming + shift + unshift
        else:
            # Well, we don't have any space it seems.
            print("No Space!")
            pass
        # TODO: Check if a car has moved into it's required position!
        for i, car in enumerate(self.queue):
            if car != None and self.id == car.end_edge and i == car.end_position:
                self.queue[i] = None
                completed_count +=1
        return completed_count
class Car():
    def __init__(self, car_id, start_edge, start_position,end_edge, end_position, path) -> None:
        self.id = car_id
        self.current_edge = start_edge
        self.current_position = start_position
        self.end_edge = end_edge
        self.end_position = end_position
        self.path = path
    def generate_path(self):
        self.path.reverse()
    def get_next_edge(self):
        if self.path == []:
            raise Exception("This Car has no where to go!")
        else:
            return self.path.pop()
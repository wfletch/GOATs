import json
from collections import defaultdict
import random
import uuid
import copy


class Network():
    """
    Global Network Object. Creates a graph from a supplied json file
    Allows the addition of new road/intersections (Edge/Vertex) and car objects on demand.
    All Control Logic passes via this node.
    """

    def __init__(self, name) -> None:
        self.id = uuid.uuid4()  # Creates a random UUID for the node
        self.edges = defaultdict(lambda: None)
        self.nodes = defaultdict(lambda: None)
        self.cars = defaultdict(lambda: None)

        # Track state of the Network.
        self.no_new_changes = False
        self.tick_count = 0
        self.completed_count = 0

        # Store Snapshots of the previous and current state
        self.previous_state = {}
        self.current_snapshot = {}
        print("USING: " + name + ".json as configuration file")
        config = None
        config_file = None
        # Open up desired config
        try:
            config_file = open('./configs/' + name + '.json')
            # TODO: Fully qualified name of the file we are loading. Not relative paths.
        except:
            raise Exception("Config Not Found!")
        try:
            # Load the config as a python dictionary. Then close
            config = json.load(config_file)
            config_file.close()
        except:
            raise Exception("Malformed Config")

        # Count Edges and nodes. not used.
        node_count = 0
        edge_count = 0

        # Create the Nodes
        for node in config["nodes"]:
            new_node = Node(node["id"], node["x"], node["y"])
            self.nodes[new_node.get_ID()] = new_node

        # Create the Edges
        for edge in config["edges"]:
            # Make sure the edges start and end node exist
            if self.nodes[edge["from"]]:
                if self.nodes[edge["to"]]:
                    new_edge = Edge(edge["id"], edge["from"],
                                    edge["to"], edge["capacity"])
                    # stitch the edges to the rquired nodes
                    from_node = self.nodes[edge["from"]]
                    from_node.add_outbound(new_edge)
                    to_node = self.nodes[edge["to"]]
                    to_node.add_inbound(new_edge)
                    self.edges[new_edge.get_ID()] = new_edge
                else:
                    raise Exception("This Edge does not have a known destination node")
            else:
                raise Exception("This Edge does not have a known origin node")
        
        # Build each car object
        for car in config["cars"]:
            car = Car(car["id"], car["start_edge"], car["start_position"],
                      car["end_edge"], car["end_position"], car["path"])
            car.generate_path()
            start_edge = self.edges[car.current_edge]
            if not start_edge.place_car_at_point(car.current_position, car):
                # Die if we fail for whatever reason.
                raise Exception(
                    "We failed to place a pre-defined car!!!! Check Config!. Car_ID: ", car.id)
            self.cars[car.id] = car
        print("Network Created")

    def setup(self):
        # DO NOT RUN!!!
        # We Want to setup a zeromq instance to push data to the visualizer!
        # This is for veresion 1,000.000
        ioloop.install()

    def tick(self):
        # Tick. On each tick the number of completed cars is returned to the caller.
        self.tick_count += 1
        order = list(self.nodes.keys())
        # random.shuffle(order)
        for node_id in order:
            node = self.nodes[node_id]
            # For each 1 network tick, trigger Node ticks
            self.completed_count += (node.tick())

    def create_snapshot(self):
        # 1. Get State of system and flatten all objects
        # 2. Save as output json
        cars_serialized = []
        nodes_serialized = []
        edges_serialized = []
        self.previous_state = self.current_snapshot
        # Get the snapshots for each Node, and Edge
        for node_key in list(self.nodes.keys()):
            node = self.nodes[node_key]
            nodes_serialized.append(node.get_snapshot())
        for edge_key in list(self.edges.keys()):
            edge = self.edges[edge_key]
            edges_serialized.append(edge.get_snapshot())
        # TODO: Materilize/Flatten Car objects
        self.current_snapshot = {
            "nodes": nodes_serialized, "edges": edges_serialized}
        # Check if the state has changed. (This is an expensive method)
        # TODO: Store change as deltas.
        if self.current_snapshot == self.previous_state:
            self.no_new_changes = True
        return self.current_snapshot

    def save_snapshot(self):
        # Save snapshot to a pre-determined location
        # TODO: Better file management
        with open('/Users/fletch/Programming/git_tree/wfletch/teraffic_visualizer-/node-ex-website/snapshots/snapshot.json', 'w') as fp:
            json.dump(self.current_snapshot, fp)
        pass

    def get_system_overview(self):
        """Return data about the system"""
        return {"Tick": self.tick_count, "Completed Count": self.completed_count}
    def has_changed(self):
        """Return True if the system has changed in the last tick, else False."""
        return not self.no_new_changes

class Node():
    def get_snapshot(self):
        res = copy.deepcopy(self.__dict__)  # EXPENSIVE!
        res["outbound_edge_id_list"] = list(
            res.pop("outbound_edges_id_to_edge", {}).keys())
        res["inbound_edge_id_list"] = list(
            res.pop("inbound_edges_id_to_edge", {}).keys())
        return res

    def __init__(self, id, x, y):
        self.x = x * 100 # These weights are for the visualizer
        self.y = y * 100
        # TODO: Make weights agnostic! (<-- seriously!!!!)
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
        """
        Node Tick
        
        Iterate through each in-bound Edge and 
        1) check if they have cars waiting to leave.
        2) activate a tick on them if they are enabled.
        """
        completed_count = 0
        order = list(self.inbound_edges_id_to_edge.keys())
        # random.shuffle(order)
        for edge_id in order:
            edge = self.inbound_edges_id_to_edge[edge_id]
            if not edge.is_active():
                continue
            if edge.has_car_waiting_to_leave():
                car = edge.pop_car_waiting_to_leave() # REMEMBER if you can't place the car, you must return it to the edge
                # Process
                # 1. Figure out car's next target edge
                # 2. Figure out if the target edge is valid, enabled, and has capacity
                # 3. If so, move the car to the target edge.
                #    If not, return the car to the edge it came from.
                target_edge_id = car.peek_next_edge()
                target_edge = self.outbound_edges_id_to_edge[target_edge_id]
                if target_edge == None:
                    raise Exception("Invalid Edge Selected! PANIC!")
                if target_edge.is_active() and target_edge.has_space_for_new_car():
                    # We have already checked to see if there is space on the target edge
                    target_edge.add_new_car(car)
                    car.pop_next_edge() # Car's destination edges are stored as a stack. Remove the point we have just moved to!
                else:
                    # Return car to edge if we are unable to place it
                    edge.return_car_to_head(car)
            completed_count += edge.tick()
        return completed_count


class Edge():
    """
    Edge

    Carries a select number of cars on it. Handles the movement of all contianed cars using it's tick function
    TODO: Actually learn how to write pydocs.
    """
    def get_snapshot(self):
        # Generate a JSON representation of the object
        # Process:
        # 1. Copy the current dictionary represenation of the edge
        # 2. Flatten all references to other objects

        # Copy the current representation as a dict
        res = copy.deepcopy(self.__dict__)  # EXPENSIVE!

        # Remove the queue to process.
        queue_to_process = res.pop("queue", []) 

        # Process the queue (Flatten each car object)
        for index, element in enumerate(queue_to_process):
            if element == None:
                continue
                # All Good, No Problem
            else:
                # Instead of contianing a pointer to the car object, just hold the cars ID
                queue_to_process[index] = queue_to_process[index].id
                # TODO: Fleshen/Flatten/Resolve the car object more!
        res["from"] = res.pop("from_node", None)
        res["to"] = res.pop("to_node", None)
        # reassign the queue
        res["queue"] = queue_to_process
        # TODO: This should all be shifted to the Front End! This is not the job of the back end.
        res["width"] = sum([entry != None for entry in self.queue])
        return res

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
        # TODO: Question if we need a deepcopy or not.
        car = copy.deepcopy(self.queue[-1])
        self.queue[-1] = None
        return car

    def return_car_to_head(self, car):
        self.place_car_at_point(len(self.queue)-1, car, force=True)

    def place_car_at_point(self, location, car, force=False):
        """Specify a location to place the car at. Force=True will overwrite whatever was there"""
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
        # This uses a 3 queue splitting technique to shift all cars up
        # 1. Find first instance of a None from the reverse.
        located_index = None
        for i in range(len(self.queue)-1, -1, -1):
            if self.queue[i] == None:
                located_index = i
                break
        if located_index != None:
            # We have found the None
            # 2. Everything before this point should be shifted
            unshift = self.queue[located_index+1::]
            shift = self.queue[0:located_index]
            incoming = [copy.deepcopy(self.incoming_car)]
            self.incoming_car = None
            self.queue = incoming + shift + unshift
        else:
            # Well, we don't have any space it seems.
            print("No Space!")
        # Check if a Car has moved into it's required position!
        for i, car in enumerate(self.queue):
            if car != None and self.id == car.end_edge and i == car.end_position:
                self.queue[i] = None
                completed_count += 1
        return completed_count # This value bubbles up to the calling object (Node) which bubbles the result up to the Network.


class Car():
    def __init__(self, car_id, start_edge, start_position, end_edge, end_position, path) -> None:
        self.id = car_id
        self.current_edge = start_edge
        self.current_position = start_position
        self.end_edge = end_edge
        self.end_position = end_position
        self.path = path

    def generate_path(self):
        self.path.reverse()

    def peek_next_edge(self):
        if self.path == []:
            raise Exception("This Car has no where to go!")
        return self.path[-1]

    def pop_next_edge(self):
        if self.path == []:
            raise Exception("This Car has no where to go!")
        else:
            return self.path.pop()

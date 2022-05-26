import json
from collections import defaultdict
class Network():
    """
    Global Network Object. Creates a graph from a supplied json file
    Allows the addition of new road/intersections (Edge/Vertex) and car objects on demand.
    """
    edges = {}
    nodes = {}
    cars = {}
    def __init__(self, name) -> None:
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
        for edge in config["edges"]:
            self.create_edge(edge)
        # Build Each Node
        # Build Each Edge
class Node():
    def __init__(self, id):
        self.inbound_edges_id_to_edge = defaultdict(lambda: None)
        self.outbound_edges = defaultdict(lambda: None)
        self.id = id
    pass
class Edge():
    def __init__(self, id, from_node, to_node, capacity):
        self.id = id
        self.from_node = from_node
        self.to_node = to_node
        self.queue = [None] * capacity
        self.incoming_car = None
    def __len__(self):
        return len(self.queue)
    def tick(self):
        pass
class Car():
    pass
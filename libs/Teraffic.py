import json
from collections import defaultdict
from re import I
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
class Edge():
    def __init__(self, from_node, to_node, capacity=2):
        self.id = id
        self.from_node = from_node
        self.to_node = to_node
        self.queue = [None] * capacity
        self.incoming_car = None
    def get_to_node(self):
        return self.to_node
    def get_from_node(self):
        return self.from_node
    def __len__(self):
        return len(self.queue)
    def get_ID(self):
        return self.id
    def tick(self):
        pass
class Car():
    pass
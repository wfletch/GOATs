from libs.Teraffic import *
import sys
if __name__ == "__main__":
    print("Teraffic Network Simulation")
    name = sys.argv[1]
    if name == None:
        raise Exception("Please Provide the name of a config!")
    network = Network(name)
    
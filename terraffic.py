from libs.Teraffic import *
import sys
if __name__ == "__main__":
    print("Teraffic Network Simulation")
    name = sys.argv[1]
    mode = sys.argv[2]
    enabled_modes = ["manual", "auto"]
    mode = mode.lower()
    if mode not in enabled_modes:
        raise Exception("Invalid Mode. Valid Modes are {}".format(enabled_modes))
    if name == None:
        raise Exception("Please Provide the name of a config!")
    print("Building: {} with Mode: {}".format(name, mode))
    network = Network(name)
    print(network)
    if mode == "auto":
        ticks = int(sys.argv[3])
        if ticks < 1:
            ticks = 1
        for _ in range(ticks):
            network.tick()
    elif mode == "manual":
        while True:
            user_input = input("Continue? (Y/N):\t")
            if user_input.upper() == "N":
                break
            if user_input.upper() == "Y":
                network.tick()
                print(network.get_system_overview())
            else:
                continue


    
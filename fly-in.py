from map_parser import Parser
from sys import argv, exit
from drone_network import DroneNetwork
from simulation import Simulator


def main() -> None:

    if len(argv) != 2:
        print("Usage: python3 map_parser.py <map_file>")
        exit(1)

    parser: Parser = Parser(map=argv[1])
    map = parser.parse()

    graph: DroneNetwork = DroneNetwork(map)
    # path = graph.path_finding(map.start_hub.name, map.end_hub.name)
    #     for zone in path:
    #         print(zone)
    paths = graph.k_shortest_paths(map.start_hub.name, map.end_hub.name, 100)

    for path in paths:
        for zone in path:
            print(zone)
            if zone == map.end_hub:
                print()

    sim = Simulator(map, 3)
    sim.simulate()
    print(f"\n{len(paths)}")

if __name__ == "__main__":
    main()

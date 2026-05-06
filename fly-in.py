from map_parser import Parser
from sys import argv
from drone_network import DroneNetwork
from drone import Drone


def main() -> None:

    if len(argv) != 2:
        print("Usage: python3 map_parser.py <map_file>")
        exit(1)

    parser: Parser = Parser(map=argv[1])
    #print(parser.parse())
    map = parser.parse()
    graph: DroneNetwork = DroneNetwork(map)
    # path = graph.path_finding(map.start_hub.name, map.end_hub.name)
    #     for zone in path:
    #         print(zone)
    paths = graph.k_shortest_paths(map.start_hub.name, map.end_hub.name, 10)

    for path in paths:
        for zone in path:
            print(zone)
            if zone == map.end_hub:
                print()

    drone_list: list[Drone] = []
    for n in range(1, map.nb_drones + 1):

        drone_list.append(Drone(n, map.start_hub.name))


if __name__ == "__main__":
    main()

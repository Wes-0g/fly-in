from drone import Drone
from drone_network import DroneNetwork
from map_parser import Map, Zone


class Simulator:

    def __init__(self, map: Map, k: int) -> None:
        self.map: Map = map
        self.drone_network: DroneNetwork = DroneNetwork(map)
        self.drones: list[Drone] = [
            Drone(n, map.start_hub.name) for n in range(1, map.nb_drones + 1)
        ]

        self.zones_count: dict[str, int] = {
            zone.name: 0 for zone in map.zones
        }

        self.zones_count[map.start_hub.name] = self.map.nb_drones
        self.links_count: dict[tuple[str, str], int] = {
            (conn.zone_a, conn.zone_b): 0 for conn in map.connections
        }

        self.current_turn: int = 0

        self.paths: list[list[Zone]] = self.drone_network.k_shortest_paths(
            map.start_hub.name, map.end_hub.name, k)

    def simulate(self) -> None:

        while not all(drone.arrived() for drone in self.drones):
            pass
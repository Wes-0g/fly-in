from drone import Drone, DroneState
from drone_network import DroneNetwork
from map_parser import Map, Zone


class Simulator:

    def __init__(self, map: Map, k: int) -> None:
        self.map: Map = map
        self.drone_network: DroneNetwork = DroneNetwork(map)
        self.waiting_drones: list[Drone] = []
        self.current_turn: int = 0

        self.zones_count: dict[str, int] = {
            zone.name: 0 for zone in self.drone_network.all_zones
        }

        self.zones_count[map.start_hub.name] = self.map.nb_drones
        self.links_count: dict[tuple[str, ...], int] = {
            tuple(sorted((conn.zone_a, conn.zone_b))): 0
            for conn in map.connections
        }

        self.paths: list[list[Zone]] = self.drone_network.k_shortest_paths(
            map.start_hub.name, map.end_hub.name, k)

        self.waiting_drones: list[Drone] = [
            Drone(i + 1, self.paths[i % len(self.paths)]) for i in range(self.map.nb_drones)
        ]

        self.active_drones: list[Drone] = []
        self.arrived_drones: list[Drone] = []

    def launch_waiting_drones(self) -> list[Drone]:
        launched_drones: list[Drone] = []
        for drone in self.waiting_drones:
            current_zone = drone.current_zone
            next_zone = drone.next_zone
            if not next_zone:
                continue

            edge = tuple(sorted((current_zone.name, next_zone.name)))
            conn = self.drone_network.get_connection(current_zone.name, next_zone.name)
            zone_availability = self.zones_count[next_zone.name] < next_zone.max_drones
            edge_availability = self.links_count[edge] < conn.max_link_capacity

            if zone_availability and edge_availability:
                self.zones_count[current_zone.name] -= 1
                self.zones_count[next_zone.name] += 1
                self.links_count[edge] += 1
                drone.move()
                drone.state = DroneState.MOVING
                launched_drones.append(drone)

        for drone in launched_drones:
            self.waiting_drones.remove(drone)
            self.active_drones.append(drone)

        return launched_drones

    def move_active_drones(self, drones: list[Drone]) -> list[Drone]:
        moved_drones: list[Drone] = []
        sorted_drones = sorted(drones, key=lambda drone: drone.path_index, reverse=True)


    def simulate(self) -> None:
        pass

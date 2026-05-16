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

    def move_drones(self, active_drones: list[Drone]) -> list[Drone]:
        moved_drones: list[Drone] = []

        all_drones: list[Drone] = sorted(
            active_drones + self.waiting_drones,
            key=lambda drone: drone.path_index,
            reverse=True
        )

        for drone in all_drones:
            if drone.arrived:
                continue
            current_zone = drone.current_zone
            next_zone = drone.next_zone
            if not next_zone:
                continue

            edge = tuple(sorted((current_zone.name, next_zone.name)))
            conn = self.drone_network.get_connection(current_zone.name, next_zone.name)

            if (self.zones_count[next_zone.name] < next_zone.max_drones
                    and self.links_count[edge] < conn.max_link_capacity):

                if drone in self.active_drones:
                    self.zones_count[current_zone.name] -= 1

                self.zones_count[next_zone.name] += 1
                self.links_count[edge] += 1
                moved_drones.append(drone)

        for drone in moved_drones:
            drone.move()

            if drone.arrived:
                self.active_drones.remove(drone)
                self.arrived_drones.append(drone)
                drone.state = DroneState.ARRIVED

            elif drone in self.waiting_drones:
                self.waiting_drones.remove(drone)
                self.active_drones.append(drone)
                drone.state = DroneState.MOVING

            else:
                drone.state = DroneState.MOVING

        return moved_drones

    def simulate(self) -> None:

        while self.active_drones or self.waiting_drones:
            moves: list[str] = []

            self.zones_count[self.map.end_hub.name] = 0

            self.links_count: dict[tuple[str, str], int] = {
                tuple(sorted((conn.zone_a, conn.zone_b))): 0
                for conn in self.map.connections
            }

            for drone in self.active_drones:
                if not drone.arrived:
                    drone.state = DroneState.WAITING

            current_active_drones = self.active_drones.copy()
            moves_drones = self.move_drones(current_active_drones)

            for drone in moves_drones:
                moves.append(f"D{drone.id}-{drone.current_zone.name}")

            self.current_turn += 1
            if moves:
                print(f"[T{self.current_turn}] {' '.join(moves)}")

        print()
        print(self.current_turn)

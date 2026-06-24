from drone import Drone, DroneState
from drone_network import DroneNetwork
from models import Map, Zone, ZoneType
from colorize import colorize


class Simulator:
    """Simulates drone movement across a network of zones.

    Attributes:
        map: The map containing zones and connections.
        drone_network: Network manager for path finding.
        current_turn: Current simulation turn number.
        zones_occupation: Dictionary tracking drone count per zone.
        links_occupation: Dictionary tracking drone count per connection.
        paths: List of available paths for drones.
        waiting_drones: List of drones waiting to start.
        active_drones: List of drones currently moving.
        arrived_drones: List of drones that have arrived.
    """

    def __init__(self, map: Map) -> None:
        """Initialize the Simulator with a map.

        Args:
            map: The map containing zones and connections for simulation.

        Raises:
            ValueError: If no valid paths exist between start and end hubs.
        """
        self.map: Map = map
        self.map.end_hub.max_drones = self.map.nb_drones
        self.drone_network: DroneNetwork = DroneNetwork(map)
        self.current_turn: int = 0

        self.zones_occupation: dict[str, int] = {
            zone.name: 0 for zone in self.drone_network.all_zones
        }

        self.zones_occupation[map.start_hub.name] = self.map.nb_drones
        self.links_occupation: dict[tuple[str, ...], int] = {
            tuple(sorted((conn.zone_a, conn.zone_b))): 0
            for conn in map.connections
        }

        self.paths: list[list[Zone]] = self.drone_network.k_shortest_paths(
            map.start_hub.name, map.end_hub.name, 2)

        if not self.paths:
            raise ValueError("Error initializing simulation"
                             "\ncause: no valid paths found "
                             "between start and end hubs")

        self.waiting_drones: list[Drone] = [
            Drone(i + 1, self.paths[i % len(self.paths)]
                  ) for i in range(self.map.nb_drones)
        ]

        self.active_drones: list[Drone] = []
        self.arrived_drones: list[Drone] = []

    def move_drones(self, active_drones: list[Drone]) ->\
            list[tuple[Drone, str]]:
        """Move drones according to their paths and zone/link constraints.

        Args:
            active_drones: List of drones currently in the network.

        Returns:
            List of tuples containing moved drones and their movement messages.
        """
        moved_drones: list[tuple[Drone, str]] = []

        all_drones: list[Drone] = sorted(
            active_drones + self.waiting_drones,
            key=lambda drone: drone.id,
            reverse=False
        )

        for drone in all_drones:

            if drone.arrived:
                continue
            current_zone = drone.current_zone
            next_zone = drone.next_zone
            if not next_zone:
                continue

            edge = tuple(sorted((current_zone.name, next_zone.name)))
            conn = self.drone_network.get_connection(
                current_zone.name, next_zone.name)

            if drone.is_restricted:
                drone.is_restricted = False
                moved_drones.append((
                    drone, f"D{drone.id}-"
                           f"{colorize(next_zone.name, next_zone.color)}"))
                continue

            if next_zone.zone == ZoneType.RESTRICTED:
                if (self.zones_occupation[next_zone.name]
                        < next_zone.max_drones
                        and self.links_occupation[edge]
                        < conn.max_link_capacity):

                    drone.is_restricted = True
                    self.links_occupation[edge] += 1
                    self.zones_occupation[next_zone.name] += 1
                    self.zones_occupation[current_zone.name] -= 1

                    moved_drones.append((
                        drone, f"D{drone.id}-"
                               f"{'-'.join(drone.current_connection)}"))
                    continue

            if (self.zones_occupation[next_zone.name]
                    < next_zone.max_drones
                    and self.links_occupation[edge]
                    < conn.max_link_capacity):

                self.zones_occupation[current_zone.name] -= 1
                self.zones_occupation[next_zone.name] += 1
                self.links_occupation[edge] += 1
                moved_drones.append((
                    drone, f"D{drone.id}-"
                           f"{colorize(next_zone.name, next_zone.color)}"))

        for drone, _ in moved_drones:
            drone.move()

            if drone.arrived:
                if drone in self.active_drones:
                    self.active_drones.remove(drone)
                elif drone in self.waiting_drones:
                    self.waiting_drones.remove(drone)
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
        """Run the simulation until all drones arrive at the destination.

        Processes each turn by moving drones according to constraints
        and printing movement information.
        """

        while self.active_drones or self.waiting_drones:
            moves: list[str] = []

            self.links_occupation = {
                tuple(sorted((conn.zone_a, conn.zone_b))): 0
                for conn in self.map.connections
            }

            for drone in self.active_drones:
                if not drone.arrived:
                    drone.state = DroneState.WAITING
                if drone.is_restricted:
                    if drone.next_zone is None:
                        continue
                    edge = tuple(sorted((
                        drone.current_zone.name, drone.next_zone.name)))
                    self.links_occupation[edge] += 1

            moves_drones: list[
                tuple[Drone, str]] = self.move_drones(self.active_drones)

            for _, msg in moves_drones:
                moves.append(msg)
            self.current_turn += 1
            if moves:
                print(f"[T{self.current_turn}] {' '.join(moves)}")

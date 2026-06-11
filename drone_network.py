from map_parser import Map, Zone, Connection, ZoneType
from heapq import heappop, heappush
from typing import Optional
from math import inf


class DroneNetwork:

    def __init__(self, map: Map) -> None:

        self.map: Map = map
        self.all_zones: list[Zone] = [self.map.start_hub,
                                      self.map.end_hub] + self.map.zones

        self.nodes: dict[str, Zone] = {
            zone.name: zone for zone in self.all_zones
        }

        self.adjacency: dict[str, list[tuple[str, Connection]]] = {
            zone.name: [] for zone in self.all_zones
        }

        for conn in self.map.connections:
            self.adjacency[conn.zone_a].append((conn.zone_b, conn))
            self.adjacency[conn.zone_b].append((conn.zone_a, conn))

    def get_connection(self, zone_a: str, zone_b: str) -> Connection:
        for neighbor, conn in self.adjacency[zone_a]:
            if neighbor == zone_b:
                return conn
        raise ValueError(f"No connection between {zone_a} and {zone_b}")

    def movement_cost(self, zone: str) -> float:
        return self.nodes[zone].zone.movement_cost()

    def path_finding(self, start: str, end: str,
                     penalties: dict[str, float] = None) -> list[Zone]:

        distances: dict[str, float] = {node: inf for node in self.nodes}
        previous: dict[str, str | None] = {node: None for node in self.nodes}

        distances[start] = 0
        priority_queue: list[tuple[float, int, str]] = [(0, 1, start)]
        while priority_queue:
            distance, _, current = heappop(priority_queue)

            if distance > distances[current]:
                continue
            if current == end:
                break

            for neighbor, conn in self.adjacency[current]:

                if self.nodes[neighbor].zone == ZoneType.BLOCKED:
                    continue

                new_cost = distance + self.movement_cost(neighbor)
                if penalties and neighbor in penalties:
                    new_cost += penalties[neighbor]

                if new_cost < distances[neighbor]:
                    distances[neighbor] = new_cost
                    previous[neighbor] = current
                    is_priority: int = 0 if (self.nodes[neighbor].zone.value
                                             == "priority") else 1
                    heappush(priority_queue, (new_cost, is_priority, neighbor))

        path: list[Zone] = []
        if distances[end] == inf:
            raise ValueError("No path found")

        current2: str | None = end
        while current2 is not None:
            path.append(self.nodes[current2])
            current2 = previous[current2]
        path.reverse()
        return path

    def k_shortest_paths(self, start: str, end: str, k: int)\
            -> list[list[Zone]]:

        try:
            short_path: list[Zone] = self.path_finding(start, end)
        except ValueError:
            return []

        candidate_short_paths: list[list[Zone]] = [short_path]
        seen: set[tuple[str, ...]] = {tuple(zone.name for zone in short_path)}

        penalties: dict[str, float] = {}

        for _ in range(k - 1):

            for path in candidate_short_paths:
                for zone in path[1:-1]:
                    penalties[zone.name] = penalties.get(zone.name, 0) + 10 # penalty

            try:
                new_path = self.path_finding(start, end, penalties)
            except ValueError:
                break

            key = tuple(zone.name for zone in new_path)
            if key not in seen:
                seen.add(key)
                candidate_short_paths.append(new_path)

        return candidate_short_paths

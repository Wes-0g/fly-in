from map_parser import Map, Zone, Connection, ZoneType
from heapq import heappop, heappush
from math import inf


class Graph:

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

    def movement_cost(self, zone: str) -> float:
        return self.nodes[zone].zone.movement_cost()

    def path_finding(self, start: str, end: str) -> list[Zone] | None:
        distances: dict[str, float] = {node: inf for node in self.nodes}
        reverse_path: dict[str, str | None] = {node: None for node in self.nodes}

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

                if new_cost < distances[neighbor]:
                    distances[neighbor] = new_cost
                    reverse_path[neighbor] = current
                    is_priority: int = 0 if (self.nodes[neighbor].zone
                                             == ZoneType.PRIORITY) else 1
                    heappush(priority_queue, (new_cost, is_priority, neighbor))

        path: list[Zone] = []
        if distances[end] == inf:
            return None

        current2: str | None = end
        while current2 is not None:
            path.append(self.nodes[current2])
            current2 = reverse_path[current2]
        path.reverse()
        return path

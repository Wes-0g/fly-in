from map_parser import Map, Zone, Connection


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

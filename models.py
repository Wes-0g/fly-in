from enum import Enum
from typing import Optional
from sys import exit
from math import inf

try:
    from pydantic import (BaseModel, Field,
                          model_validator)
except ModuleNotFoundError:
    print("Make install First to install dependencies")
    exit(1)


class ZoneType(Enum):
    RESTRICTED = "restricted"
    NORMAL = "normal"
    PRIORITY = "priority"
    BLOCKED = "blocked"

    def movement_cost(self) -> float:

        cost: dict[ZoneType, float] = {ZoneType.NORMAL: 1,
                                       ZoneType.PRIORITY: 1,
                                       ZoneType.RESTRICTED: 2,
                                       ZoneType.BLOCKED: inf}
        return cost[self]


class Zone(BaseModel):

    name: str
    x: int
    y: int
    zone: ZoneType = Field(default=ZoneType.NORMAL)
    color: Optional[str] = Field(default=None)
    max_drones: int = Field(default=1, ge=1)
    line: str

    @model_validator(mode='after')
    def name_validator(self) -> "Zone":
        if ' ' in self.name or '-' in self.name:
            raise ValueError(f"Error parsing line: '{self.line}'"
                             f"\ncause: spaces or dashes are in zone name"
                             f"\ngot: '{self.name}'")
        return self


class Connection(BaseModel):

    zone_a: str
    zone_b: str
    max_link_capacity: int = Field(default=1, ge=1)
    line: str

    @model_validator(mode='after')
    def zones_validator(self) -> "Connection":
        if ' ' in self.zone_a or '-' in self.zone_a:
            raise ValueError(f"Error parsing line: '{self.line}'"
                             f"\ncause: spaces or dashes in zone name"
                             f"\ngot: '{self.zone_a}'")

        if ' ' in self.zone_b or '-' in self.zone_b:
            raise ValueError(f"Error parsing line: '{self.line}'"
                             f"\ncause: spaces or dashes in zone name"
                             f"\ngot: '{self.zone_b}'")
        if self.zone_a == self.zone_b:
            raise ValueError(f"Error parsing line: '{self.line}'"
                             f"\ncause: zone_a and zone_b must be different"
                             f"\ngot: zone_a='{self.zone_a}', zone_b='{self.zone_b}'")
        return self


class Map(BaseModel):
    nb_drones: int = Field(ge=1)
    start_hub: Zone
    end_hub: Zone
    zones: list[Zone]
    connections: list[Connection]

    @model_validator(mode='after')
    def duplicates_zones_validator(self) -> "Map":
        if self.start_hub.name == self.end_hub.name:
            raise ValueError(f"Error parsing line: {self.start_hub.line}"
                             f"\ncause: start_hub and end_hub must be different"
                             f"\ngot: start_hub='{self.start_hub.name}', end_hub='{self.end_hub.name}'")

        seen: list[str] = []
        duplicates: list[str] = []
        for zone in self.zones:
            if zone.name in seen:
                duplicates.append(zone.name)
            else:
                seen.append(zone.name)

        if self.start_hub.name in seen:
            duplicates.append(self.start_hub.name)
        if self.end_hub.name in seen:
            duplicates.append(self.end_hub.name)
        if duplicates:
            raise ValueError(f"Error parsing line: {duplicates[0]}"
                             f"\ncause: duplicate zone names found"
                             f"\ngot: {duplicates}")
        return self

    @model_validator(mode='after')
    def valid_zone_connections(self) -> "Map":

        zones: set[str] = {zone.name for zone in self.zones}
        zones.add(self.start_hub.name)
        zones.add(self.end_hub.name)
        connection_a: list[str] = [conn.zone_a for conn in self.connections]
        connection_b: list[str] = [conn.zone_b for conn in self.connections]
        connections: set[str] = set(connection_a + connection_b)

        invalid = list(connections - zones)
        if invalid:
            raise ValueError(f"Error parsing line: connection: {invalid[0]}-{invalid[1]}"
                             f"\ncause: invalid zone names in connections"
                             f"\ngot: {invalid}")
        return self

    @model_validator(mode='after')
    def duplicate_connections_validator(self) -> "Map":
        connections: list[tuple[str, str]] = [
            (conn.zone_a, conn.zone_b) for conn in self.connections
        ]

        seen_connections: set[tuple[str, str]] = set()
        for conn_a, conn_b in connections:
            reverse_conn: tuple[str, str] = (conn_b, conn_a)
            if ((conn_a, conn_b) in seen_connections
                    or reverse_conn in seen_connections):
                raise ValueError(f"Error parsing line: connection:{conn_a}-{conn_b}"
                                 f"\ncause: duplicate connection found"
                                 f"\ngot: {conn_a}-{conn_b}")
            seen_connections.add((conn_a, conn_b))

        return self

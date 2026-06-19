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
    """Enumeration of zone types with different movement costs.

    Attributes:
        RESTRICTED: Zone with restricted access (cost: 2).
        NORMAL: Standard zone (cost: 1).
        PRIORITY: Priority zone (cost: 1).
        BLOCKED: Impassable zone (cost: infinity).
    """
    RESTRICTED = "restricted"
    NORMAL = "normal"
    PRIORITY = "priority"
    BLOCKED = "blocked"

    def movement_cost(self) -> float:
        """Get the movement cost for this zone type.

        Returns:
            The movement cost as a float. BLOCKED zones return infinity.
        """

        cost: dict[ZoneType, float] = {ZoneType.NORMAL: 1,
                                       ZoneType.PRIORITY: 1,
                                       ZoneType.RESTRICTED: 2,
                                       ZoneType.BLOCKED: inf}
        return cost[self]


class Zone(BaseModel):
    """Represents a zone in the drone network.

    Attributes:
        name: Unique identifier for the zone.
        x: X coordinate of the zone.
        y: Y coordinate of the zone.
        zone: Type of the zone (default: NORMAL).
        color: Display color for the zone (optional).
        max_drones: Maximum number of drones allowed in the zone.
        line: Original line from the map file for error reporting.
    """

    name: str
    x: int
    y: int
    zone: ZoneType = Field(default=ZoneType.NORMAL)
    color: Optional[str] = Field(default=None)
    max_drones: int = Field(default=1)
    line: str

    @model_validator(mode='after')
    def name_validator(self) -> "Zone":
        """Validate that zone name contains no spaces or dashes.

        Returns:
            The validated Zone object.

        Raises:
            ValueError: If the name contains spaces or dashes.
        """
        if ' ' in self.name or '-' in self.name:
            raise ValueError(f"Error parsing line: '{self.line}'"
                             f"\ncause: spaces or dashes are in zone name"
                             f"\ngot: '{self.name}'")
        return self

    @model_validator(mode='after')
    def max_drones_metadata_validator(self) -> "Zone":
        """Validate that max_drones is at least 1.

        Returns:
            The validated Zone object.

        Raises:
            ValueError: If max_drones is less than 1.
        """

        if self.max_drones < 1:
            raise ValueError(f"Error parsing line: '{self.line}'"
                             f"\ncause: max_drones must be at least 1"
                             f"\ngot: {self.max_drones}")
        return self


class Connection(BaseModel):
    """Represents a connection between two zones.

    Attributes:
        zone_a: Name of the first zone.
        zone_b: Name of the second zone.
        max_link_capacity: Maximum drones allowed on this connection.
        line: Original line from the map file for error reporting.
    """

    zone_a: str
    zone_b: str
    max_link_capacity: int = Field(default=1)
    line: str

    @model_validator(mode='after')
    def zones_validator(self) -> "Connection":
        """Validate that zone names are valid and different.

        Returns:
            The validated Connection object.

        Raises:
            ValueError: If zone names contain spaces/dashes or are identical.
        """
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
                             f"\ngot: zone_a='{self.zone_a}'"
                             f", zone_b='{self.zone_b}'")
        return self

    @model_validator(mode='after')
    def max_link_capacity_metadata_validator(self) -> "Connection":
        """Validate that max_link_capacity is at least 1.

        Returns:
            The validated Connection object.

        Raises:
            ValueError: If max_link_capacity is less than 1.
        """
        if self.max_link_capacity < 1:
            raise ValueError(f"Error parsing line: '{self.line}'"
                             f"\ncause: max_link_capacity must be at least 1"
                             f"\ngot: {self.max_link_capacity}")
        return self


class Map(BaseModel):
    """Represents the complete map for drone simulation.

    Attributes:
        nb_drones: Number of drones to simulate.
        start_hub: Starting zone for all drones.
        end_hub: Destination zone for all drones.
        zones: List of intermediate zones.
        connections: List of connections between zones.
    """
    nb_drones: int = Field(ge=1)
    start_hub: Zone
    end_hub: Zone
    zones: list[Zone]
    connections: list[Connection]

    @model_validator(mode='after')
    def duplicates_zones_validator(self) -> "Map":
        """Validate that all zone names are unique.

        Returns:
            The validated Map object.

        Raises:
            ValueError: If duplicate zone names are found.
        """
        if self.start_hub.name == self.end_hub.name:
            raise ValueError(f"Error parsing line: {self.start_hub.line}"
                             f"\ncause: start_hub and "
                             f"end_hub must be different"
                             f"\ngot: start_hub='{self.start_hub.name}',"
                             f" end_hub='{self.end_hub.name}'")

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
    def duplicate_connections_validator(self) -> "Map":
        """Validate that there are no duplicate connections.

        Returns:
            The validated Map object.

        Raises:
            ValueError: If duplicate connections
            (in either direction) are found.
        """
        connections: list[tuple[str, str]] = [
            (conn.zone_a, conn.zone_b) for conn in self.connections
        ]

        seen_connections: set[tuple[str, str]] = set()
        for conn_a, conn_b in connections:
            reverse_conn: tuple[str, str] = (conn_b, conn_a)
            if ((conn_a, conn_b) in seen_connections
                    or reverse_conn in seen_connections):
                raise ValueError(f"Error parsing line: "
                                 f"connection:{conn_a}-{conn_b}"
                                 f"\ncause: duplicate connection found"
                                 f"\ngot: {conn_a}-{conn_b}")
            seen_connections.add((conn_a, conn_b))

        return self

    @model_validator(mode='after')
    def start_end_blocked(self) -> "Map":
        """Validate that start and end hubs are not blocked.

        Returns:
            The validated Map object.

        Raises:
            ValueError: If start_hub or end_hub is BLOCKED.
        """
        if self.start_hub.zone == ZoneType.BLOCKED:
            raise ValueError(f"Error parsing line: {self.start_hub.line}"
                             f"\ncause: start_hub cannot be blocked"
                             f"\ngot: {self.start_hub.zone}")
        if self.end_hub.zone == ZoneType.BLOCKED:
            raise ValueError(f"Error parsing line: {self.end_hub.line}"
                             f"\ncause: end_hub cannot be blocked"
                             f"\ngot: {self.end_hub.zone}")
        return self

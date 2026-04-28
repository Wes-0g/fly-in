from pydantic import (BaseModel, Field,
                      model_validator,
                      ValidationError,
                      field_validator)
from enum import Enum
from typing import Optional
from sys import argv, exit


class ZoneType(Enum):
    RESTRICTED = "restricted"
    NORMAL = "normal"
    PRIORITY = "priority"
    BLOCKED = "blocked"


class Zone(BaseModel):

    name: str
    x: int
    y: int
    zone: ZoneType = Field(default=ZoneType.NORMAL)
    color: Optional[str] = Field(default=None)
    max_drones: int = Field(default=1, ge=1)

    @field_validator('name', mode='after')
    @classmethod
    def name_validator(cls, name: str) -> str:
        if ' ' in name or '-' in name:
            raise ValueError("name must not contain spaces or dashes")
        return name

    @field_validator('max_drones', mode='after')
    @classmethod
    def max_drones_validator(cls, max_drones: int) -> int:
        if max_drones < 1:
            raise ValueError("max_drones must be a positive integer")
        return max_drones


class Connection(BaseModel):

    zone_a: str
    zone_b: str
    max_link_capacity: int = Field(default=1, ge=1)

    @model_validator(mode='after')
    def zones_validator(self) -> "Connection":
        if ' ' in self.zone_a or '-' in self.zone_a:
            raise ValueError("Connection name must not "
                             "contain spaces or dashes")
        if ' ' in self.zone_b or '-' in self.zone_b:
            raise ValueError("Connection name must not "
                             "contain spaces or dashes")
        return self


class Map(BaseModel):
    nb_drones: int = Field(ge=1)
    start_hub: Zone
    end_hub: Zone
    zones: list[Zone]
    connections: list[Connection]

    @field_validator('nb_drones', mode='after')
    @classmethod
    def nb_drones_validator(cls, nb_drones: int) -> int:
        if nb_drones < 1:
            raise ValueError("nb_drones must be a positive integer")
        return nb_drones

    @model_validator(mode='after')
    def start_end_validator(self) -> "Map":
        if self.start_hub.name == self.end_hub.name:
            raise ValueError("start_hub and end_hub must be different")
        return self

    @model_validator(mode='after')
    def duplicates_validator(self) -> "Map":
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
            raise ValueError(f"Duplicate zone names: {duplicates}")
        return self

    @model_validator(mode='after')
    def valid_zone_connections(self) -> "Map":

        zones = {zone.name for zone in self.zones}
        zones.add(self.start_hub.name)
        zones.add(self.end_hub.name)
        connection_a = [conn.zone_a for conn in self.connections]
        connection_b = [conn.zone_b for conn in self.connections]
        connections: set[str] = set(connection_a + connection_b)

        if connections.difference(zones):
            raise ValueError(f"Invalid zone names in connections: "
                             f"{connections.difference(zones)}")
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
                raise ValueError(f"Duplicate connection: {conn_a}-{conn_b}")
            seen_connections.add((conn_a, conn_b))

        return self


class Parser:

    def __init__(self, map: str) -> None:
        self.map: str = map
        self.zones: list[Zone] = []
        self.connections: list[Connection] = []
        self.nb_drones: int = 0

    def filter_lines(self) -> list[str]:

        try:
            with open(self.map, 'r') as file:
                stripped_lines: list[str] = [
                    line.strip() for line in file.readlines()
                ]
                lines: list[str] = [
                    line for line in stripped_lines
                    if line and not line.startswith('#')
                ]

                if not lines:
                    raise ValueError("No valid lines found in map file")

                if not lines[0].startswith('nb_drones:'):
                    raise ValueError(f"First line must contain "
                                     f"nb_drones\ngot: {lines[0]}")

                nb_drones_count: int = 0
                start_hub_count: int = 0
                end_hub_count: int = 0

                for line in lines:
                    if line.startswith('start_hub:'):
                        start_hub_count += 1
                    elif line.startswith('end_hub:'):
                        end_hub_count += 1
                    elif line.startswith('nb_drones:'):
                        nb_drones_count += 1

                    if nb_drones_count > 1:
                        raise ValueError(f"Only one nb_drones is allowed"
                                         f"\ngot: {nb_drones_count}")

                    if start_hub_count > 1:
                        raise ValueError(f"Only one start_hub is allowed"
                                         f"\ngot: {start_hub_count}")
                    if end_hub_count > 1:
                        raise ValueError(f"Only one end_hub is allowed"
                                         f"\ngot: {end_hub_count}")

                return lines

        except ValueError as e:
            print(f"ERROR: {e}")
            exit(1)

    @staticmethod
    def nb_drones_parser(line: str) -> int:

        data: list[str] = line.split()
        if len(data) != 2:
            raise ValueError(f"Invalid nb_drones line format.\n"
                             f"Expected: 'nb_drones: <positive_integer>'\n"
                             f"Got: '{line}'")
        else:
            try:
                nb_drones: int = int(data[1])
            except ValueError:
                raise ValueError(f"Invalid nb_drones value.\n"
                                 f"Expected a positive integer,"
                                 f" got: '{data[1]}'")

        return nb_drones

    @staticmethod
    def zone_parser(line: str) -> Zone:

        if '[' in line:
            base, metadata = line.split('[')
            metadata = metadata.rstrip(']')
        else:
            base = line
            metadata = None

        try:
            _, name, x, y = base.strip().split(' ')
        except ValueError:
            raise ValueError(f"Error parsing line: '{line}'"
                             f"\nexpected: 'name x y [metadata]'")

        meta_dict: dict[str, str] = {}
        if metadata:
            for item in metadata.split():
                if item.count('=') != 1:
                    raise ValueError(f"Invalid metadata format: '{item}'")
                key, value = item.split('=')
                meta_dict[key] = value.lower()

        try:
            return Zone(name=name, x=x, y=y, **meta_dict)
        except ValidationError as e:
            raise ValueError(f"Error parsing line: {line}\n{e}")

    @staticmethod
    def connection_parser(line: str) -> Connection:

        if '[' in line:
            base, connection_metadata = line.split('[')
            connection_metadata = connection_metadata.rstrip(']')
        else:
            base = line
            connection_metadata = None

        try:
            connection = base.split()[1]
            if connection.count('-') != 1:
                raise ValueError()
            else:
                connection_a, connection_b = connection.split('-')
        except ValueError:
            raise ValueError(f"Error parsing line: '{line}"
                             f"\nexpected: <connection_a-connection_b>"
                             f" [metadata]'")

        metadata_dict: dict[str, str] = {}
        if connection_metadata:
            if connection_metadata.count('=') != 1:
                raise ValueError(f"Invalid metadata format:"
                                 f" '{connection_metadata}'")
            key, value = connection_metadata.split('=')
            metadata_dict[key] = value

        return Connection(zone_a=connection_a,
                          zone_b=connection_b, **metadata_dict) # check if the metadata is valid firsst

    def parse(self) \
            -> dict[str, int | Zone | list[Zone] | list[Connection] | None]:
        lines: list[str] = self.filter_lines()

        self.nb_drones: int = self.nb_drones_parser(lines[0])

        start = None
        end = None
        for line in lines[1:]:
            if line.startswith('start_hub:'):
                start = self.zone_parser(line)
            elif line.startswith('end_hub:'):
                end = self.zone_parser(line)
            elif line.startswith('hub:'):
                self.zones.append(self.zone_parser(line))
            elif line.startswith('connection:'):
                self.connections.append(self.connection_parser(line))
            else:
                raise ValueError(f"Invalid line: {line}")

        return {"nb_drones": self.nb_drones,
                "start_hub": start,
                "end_hub": end,
                "zones": self.zones,
                "connections": self.connections}


def main() -> None:

    if len(argv) != 2:
        print("Usage: python3 map_parser.py <map_file>")
        exit(1)
    else:
        parser: Parser = Parser(map=argv[1])
        parser.filter_lines()
        map = Map(**parser.parse())


if __name__ == "__main__":
    # try:
    main()
    # except ValueError as e:
    #     print(e.errors()[0]['msg'])
    #     exit(1)

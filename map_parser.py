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
    color: Optional[str] = None
    max_drones: int = Field(default=1, ge=1)

    @field_validator('name')
    @classmethod
    def name_validator(cls, name: str) -> str:
        if ' ' in name or '-' in name:
            raise ValueError("name must not contain spaces or dashes")
        return name

    @field_validator('max_drones')
    @classmethod
    def max_drones_validator(cls, max_drones: int) -> int:
        if max_drones < 1:
            raise ValueError("max_drones must be a positive integer")
        return max_drones


class Connection(BaseModel):

    zone_a: str
    zone_b: str
    max_link_capacity: int = Field(default=1, ge=1)

    @field_validator('zone_a')
    @classmethod
    def zone_a_validator(cls, zone_a: str) -> str:
        if ' ' in zone_a or '-' in zone_a:
            raise ValueError("Connection name must not "
                             "contain spaces or dashes")
        return zone_a

    @field_validator('zone_b')
    @classmethod
    def zone_b_validator(cls, zone_b: str) -> str:
        if ' ' in zone_b or '-' in zone_b:
            raise ValueError("Connection name must not "
                             "contain spaces or dashes")
        return zone_b


class Map(BaseModel):
    nb_drones: int = Field(ge=1)
    start_hub: Zone
    end_hub: Zone
    zones: list[Zone]
    connections: list[Connection]


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
                                 f"Expected a positive integer, got: '{data[1]}'")

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
                meta_dict[key] = value

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
                             f"\nexpected: <connection_a-connection_b> [metadata]'")

        metadata_dict: dict[str, str] = {}
        if connection_metadata:
                if connection_metadata.count('=') != 1:
                    raise ValueError(f"Invalid metadata format: '{connection_metadata}'")
                key, value = connection_metadata.split('=')
                metadata_dict[key] = value

        return Connection(zone_a=connection_a, zone_b=connection_b, **metadata_dict)

    def parse(self) -> dict[str, int | Zone | list[Zone] | list[Connection] | None]:
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
        print(parser.parse())


if __name__ == "__main__":
    main()

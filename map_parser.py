from sys import exit
from models import Map, Zone, Connection
try:
    from pydantic import ValidationError
except ModuleNotFoundError:
    print("Make install First to install dependencies")
    exit(1)


class Parser:
    """Parses map files to create Map objects for drone simulation.

    Attributes:
        map: Path to the map file to parse.
    """

    def __init__(self, map: str) -> None:
        """Initialize the Parser with a map file path.

        Args:
            map: Path to the map file to parse.
        """
        self.map: str = map

    def filter_lines(self) -> list[str]:
        """Read and filter valid lines from the map file.

        Removes comments, empty lines, and validates the file structure.
        Ensures only one nb_drones, start_hub, and end_hub line exists.

        Returns:
            List of valid, non-empty, non-comment lines from the file.

        Raises:
            ValueError: If file is empty, first line is invalid, or
                duplicate required lines are found.
        """

        with open(self.map, 'r') as file:
            stripped_lines: list[str] = [
                line.strip() for line in file.readlines()
            ]
            lines: list[str] = [
                line for line in stripped_lines
                if line and not line.startswith('#')
            ]

            if not lines:
                raise ValueError(f"Error parsing line: '{self.map}'"
                                 f"\ncause: no valid lines found"
                                 f"\ngot: empty file")

            if not lines[0].startswith('nb_drones:'):
                raise ValueError(f"Error parsing line: '{lines[0]}'"
                                 f"\ncause: first line must start "
                                 f"with 'nb_drones:'"
                                 f"\ngot: '{lines[0]}'")

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
                    raise ValueError(f"Error parsing line: '{line}'"
                                     f"\ncause: only one nb_drones is allowed"
                                     f"\ngot: {nb_drones_count} "
                                     f"nb_drones lines")

                if start_hub_count > 1:
                    raise ValueError(f"Error parsing line: '{line}'"
                                     f"\ncause: only one start_hub is allowed"
                                     f"\ngot: {start_hub_count} "
                                     f"start_hub lines")
                if end_hub_count > 1:
                    raise ValueError(f"Error parsing line: '{line}'"
                                     f"\ncause: only one end_hub is allowed"
                                     f"\ngot: {end_hub_count} end_hub lines")

            return lines

    @staticmethod
    def nb_drones_parser(line: str) -> int:
        """Parse the nb_drones line to extract the number of drones.

        Args:
            line: The nb_drones line to parse.

        Returns:
            The number of drones as an integer.

        Raises:
            ValueError: If line format is invalid or value is not an integer.
        """

        if '#' in line:
            line = line[:line.index('#')].strip()

        data: list[str] = line.split()
        if len(data) != 2:
            raise ValueError(f"Error parsing line: '{line}'"
                             f"\ncause: invalid nb_drones line format"
                             f"\ngot: '{line}'")
        else:
            try:
                nb_drones: int = int(data[1])
            except ValueError:
                raise ValueError(f"Error parsing line: '{line}'"
                                 f"\ncause: invalid nb_drones value"
                                 f"\ngot: '{data[1]}'")
        if nb_drones < 1:
            raise ValueError(f"Error parsing line: '{line}'"
                             f"\ncause: nb_drones must be a positive integer"
                             f"\ngot: '{nb_drones}'")
        return nb_drones

    @staticmethod
    def zone_parser(line: str) -> Zone:
        """Parse a zone line to create a Zone object.

        Args:
            line: The zone line to parse.

        Returns:
            A Zone object with parsed attributes.

        Raises:
            ValueError: If zone format, metadata, or coordinates are invalid.
        """

        parts: list[str] = line.split()

        if len(parts) < 4:
            raise ValueError(f"Error parsing line: '{line}'"
                             f"\ncause: invalid zone format"
                             f"\ngot: '{line}'")

        _, name, x, y = parts[0], parts[1], parts[2], parts[3]
        rest: list[str] = parts[4:]

        metadata: str | None = None
        if rest:
            meta_block: str = ' '.join(rest)
            if meta_block.count('[') != 1 or meta_block.count(']') != 1:
                raise ValueError(f"Error parsing line: '{line}'"
                                 f"\ncause: metadata must be a [...] block"
                                 f"\ngot: '{meta_block}'")
            if not meta_block.startswith('[') or not meta_block.endswith(']'):
                raise ValueError(f"Error parsing line: '{line}'"
                                 f"\ncause: invalid zone format"
                                 f"\ngot: '{meta_block}'")

            metadata = meta_block[1:-1]

        meta_dict: dict = {}
        if metadata:
            if metadata.count('=') > 3:
                raise ValueError(f"Error parsing line: '{line}'"
                                 f"\ncause: too many metadata key-value pairs"
                                 f"\ngot: '{metadata}'")
            for item in metadata.split():
                if item.count('=') != 1:
                    raise ValueError(f"Error parsing line: '{line}'"
                                     f"\ncause: invalid metadata format"
                                     f"\ngot: '{item}'")

                key, value = item.split('=')
                value = value.strip().lower()
                key = key.strip().lower()

                if key in meta_dict:
                    raise ValueError(f"Error parsing line: '{line}"
                                     f"\ncause: duplicate key '{key}'"
                                     f"\ngot: '{line}'")

                if key not in ['zone', 'color', 'max_drones']:
                    raise ValueError(f"Error parsing line: '{line}"
                                     f"\ncause: invalid metadata key"
                                     f"\ngot: '{key}'")
                if key == "max_drones":
                    try:
                        _ = int(value)
                    except ValueError:
                        raise ValueError(f"Error parsing line: '{line}"
                                         f"\ncause: invalid metadata value"
                                         f"\ngot: '{value}'")

                if key == "color":
                    if not value.isalpha():
                        raise ValueError(f"Error parsing line: '{line}"
                                         f"\ncause: invalid metadata value"
                                         f"\ngot: '{value}'")

                if not value:
                    raise ValueError(f"Error parsing line: '{line}"
                                     f"\ncause: invalid metadata value"
                                     f"\ngot: '{value}'")

                meta_dict[key] = value

        zones_type: list[str] = ['restricted', 'normal', 'priority', 'blocked']
        if 'zone' in meta_dict:
            if meta_dict['zone'] not in zones_type:
                raise ValueError(f"Error parsing line: '{line}'"
                                 f"\ncause: invalid zone type"
                                 f"\ngot: '{meta_dict['zone']}'")

        try:
            xi, yi = int(x), int(y)
        except ValueError:
            raise ValueError(f"Error parsing line: '{line}'"
                             f"\ncause: invalid zone coordinates"
                             f"\ngot: x='{x}', y='{y}'")

        try:
            return Zone(line=line, name=name, x=xi, y=yi, **meta_dict)
        except ValidationError as e:
            raise ValueError(f"{e.errors()[0]['msg'].lstrip('Value error, ')}")

    @staticmethod
    def connection_parser(line: str) -> Connection:
        """Parse a connection line to create a Connection object.

        Args:
            line: The connection line to parse.

        Returns:
            A Connection object with parsed attributes.

        Raises:
            ValueError: If connection format or metadata is invalid.
        """

        parts: list[str] = line.split()

        if len(parts) < 2:
            raise ValueError(f"Error parsing line: '{line}'"
                             f"\ncause: invalid connection format"
                             f"\ngot: '{line}'")
        connection: str = parts[1]
        rest: list[str] = parts[2:]

        connection_metadata: str | None = None
        if rest:
            meta_block: str = ' '.join(rest)
            if meta_block.count('[') != 1 or meta_block.count(']') != 1:
                raise ValueError(f"Error parsing line: '{line}'"
                                 f"\ncause: metadata must be a [...] block"
                                 f"\ngot: '{meta_block}'")

            if not meta_block.startswith('[') or not meta_block.endswith(']'):
                raise ValueError(f"Error parsing line: '{line}'"
                                 f"\ncause: invalid connection format"
                                 f"\ngot: '{meta_block}'")
            connection_metadata = meta_block[1:-1]

        if connection.count('-') != 1:
            raise ValueError(f"Error parsing line: '{line}'"
                             f"\ncause: invalid connection format, "
                             f"expected 'zoneA-zoneB'"
                             f"\ngot: '{connection}'")

        connection_a, connection_b = connection.split('-')

        metadata_dict: dict = {}
        if connection_metadata:
            if connection_metadata.count('=') != 1:
                raise ValueError(f"Error parsing line: '{line}'"
                                 f"\ncause: invalid metadata format"
                                 f"\ngot: '{connection_metadata}'")

            key, value = connection_metadata.split('=')
            if key.lower() not in ['max_link_capacity']:
                raise ValueError(f"Error parsing line: '{line}'"
                                 f"\ncause: invalid metadata key"
                                 f"\ngot: '{key}'")
            try:
                _ = int(value)
            except ValueError:
                raise ValueError(f"Error parsing line: '{line}"
                                 f"\ncause: invalid metadata value"
                                 f"\ngot: '{value}'")
            if not value:
                raise ValueError(f"Error parsing line: '{line}'"
                                 f"\ncause: invalid metadata value"
                                 f"\ngot: '{value}'")

            metadata_dict[key.lower()] = value.lower()
        try:
            return Connection(zone_a=connection_a,
                              zone_b=connection_b,
                              **metadata_dict,
                              line=line)
        except ValidationError as e:
            raise ValueError(f"{e.errors()[0]['msg'].lstrip('Value error, ')}")

    def parse(self) -> Map:
        """Parse the entire map file and create a Map object.

        Reads all lines, parses nb_drones, zones, and connections,
        and validates the complete map structure.

        Returns:
            A Map object containing all parsed data.

        Raises:
            ValueError: If required lines are missing or validation fails.
            ValidationError: If pydantic validation fails.
        """
        try:
            lines: list[str] = self.filter_lines()

            nb_drones: int = self.nb_drones_parser(lines[0])

            start: Zone | None = None
            end: Zone | None = None
            zones: list[Zone] = []
            connections: list[Connection] = []
            known_zones: set[str] = set()

            for line in lines[1:]:
                if '#' in line:
                    line = line[:line.index('#')].strip()
                line_type: str = line.split()[0]

                if line_type == 'start_hub:':
                    start = self.zone_parser(line)
                    known_zones.add(start.name)

                elif line_type == 'end_hub:':
                    end = self.zone_parser(line)
                    known_zones.add(end.name)

                elif line_type == 'hub:':
                    zone = self.zone_parser(line)
                    zones.append(zone)
                    known_zones.add(zone.name)

                elif line_type == 'connection:':
                    conn = self.connection_parser(line)
                    for name in (conn.zone_a, conn.zone_b):
                        if name not in known_zones:
                            raise ValueError(f"Error parsing line: '{line}'"
                                             f"\ncause: unknown zone"
                                             f"\ngot: '{name}'")
                    connections.append(conn)
                else:
                    raise ValueError(f"Error parsing line: '{line}'"
                                     f"\ncause: unknown line type or "
                                     f"invalid line format"
                                     f"\ngot: '{line}'")

            if not start:
                raise ValueError(f"Error parsing file: '{self.map}'"
                                 f"\ncause: start_hub line not found"
                                 f"\ngot: missing start_hub")
            if not end:
                raise ValueError(f"Error parsing file: '{self.map}'"
                                 f"\ncause: end_hub line not found"
                                 f"\ngot: missing end_hub")

            return Map(nb_drones=nb_drones,
                       start_hub=start,
                       end_hub=end,
                       zones=zones,
                       connections=connections)

        except ValidationError as e:
            print(f"{e.errors()[0]['msg'].lstrip('Value error, ')}")
            exit(1)
        except ValueError as e:
            print(f"{e}")
            exit(1)

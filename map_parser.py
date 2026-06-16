from sys import exit
from models import Map, Zone, Connection
try:
    from pydantic import ValidationError
except ModuleNotFoundError:
    print("Make install First to install dependencies")
    exit(1)


class Parser:

    def __init__(self, map: str) -> None:
        self.map: str = map

    def filter_lines(self) -> list[str]:

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

        return nb_drones

    @staticmethod
    def zone_parser(line: str) -> Zone:

        if line.count('[') == 1 and line.count(']') == 1:
            base, metadata = line.split('[')
            metadata = metadata.rstrip(']')
        else:
            base = line
            metadata = None

        try:
            _, name, x, y = base.strip().split()
        except ValueError:
            raise ValueError(f"Error parsing line: '{line}'"
                             f"\ncause: invalid zone format"
                             f"\ngot: '{line}'")

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
                if key in meta_dict:
                    raise ValueError(f"Error parsing line: '{line}"
                                     f"\ncause: duplicate key '{key}'"
                                     f"\ngot: '{line}'")
                meta_dict[key.lower()] = value.lower()

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

        if line.count('[') == 1 and line.count(']') == 1:
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
            raise ValueError(f"Error parsing line: '{line}'"
                             f"\ncause: invalid connection format"
                             f"\ngot: '{line}'")

        metadata_dict: dict = {}
        if connection_metadata:
            if connection_metadata.count('=') != 1:
                raise ValueError(f"Error parsing line: '{line}'"
                                 f"\ncause: invalid metadata format"
                                 f"\ngot: '{connection_metadata}'")
            key, value = connection_metadata.split('=')
            metadata_dict[key.lower()] = value.lower()
        try:
            return Connection(zone_a=connection_a,
                              zone_b=connection_b,
                              **metadata_dict,
                              line=line)
        except ValidationError as e:
            raise ValueError(f"{e.errors()[0]['msg'].lstrip('Value error, ')}")

    def parse(self) -> Map:
        try:
            lines: list[str] = self.filter_lines()

            nb_drones: int = self.nb_drones_parser(lines[0])

            start = None
            end = None
            zones: list[Zone] = []
            connections: list[Connection] = []
            for line in lines[1:]:
                if '#' in line:
                    line = line[:line.index('#')].strip()

                if line.startswith('start_hub:'):
                    start = self.zone_parser(line)
                elif line.startswith('end_hub:'):
                    end = self.zone_parser(line)
                elif line.startswith('hub:'):
                    zones.append(self.zone_parser(line))
                elif line.startswith('connection:'):
                    connections.append(self.connection_parser(line))
                else:
                    raise ValueError(f"Error parsing line: '{line}'"
                                     f"\ncause: unknown line type"
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
            print(f"ERROR: {e.errors()[0]['msg'].lstrip('Value error, ')}")
            exit(1)
        except ValueError as e:
            print(f"ERROR: {e}")
            exit(1)

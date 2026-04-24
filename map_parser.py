from pydantic import BaseModel, Field, model_validator, ValidationError
from enum import Enum
import sys


class Zone(Enum):
    RESTRICTED = "restricted"
    NORMAL = "normal"
    PRIORITY = "priority"
    BLOCKED = "blocked"


class Parser:

    def __init__(self, map: str) -> None:
        self.map: str = map

    def parse(self) -> dict:
        data: dict = {}
        try:
            with open(self.map, 'r') as file:
                lines: list[str] = file.readlines()
                for line in lines:
                    striped_line: str = line.strip()
                    if not striped_line or striped_line.startswith('#'):
                        continue

                    if striped_line.count(':') != 1:
                        raise ValueError(f"Expected <name> <x> <y> "
                                         f"[metadata] got {striped_line}")

                    key: str = striped_line.split(':')[0].strip()
                    value: str = striped_line.split(':')[1].strip()


                    if key == "nb_drones":
                        try:
                            data[key] = int(value)
                        except ValueError:
                            raise ValueError("nb_drones must be a positive integer")


                    if key == "start_hub":
                        name: str = value.split(' ')[0].strip()
                        try:
                            x: int = int(value.split(' ')[1])
                        except ValueError:
                            raise ValueError("x must be an integer")
                        try:
                            y: int = int(value.split(' ')[2])
                        except ValueError:
                            raise ValueError("y must be an integer")
                        metadata: str = value.split(' ', 3)[3].strip()
                        if not metadata.startswith('[') or not metadata.endswith(']'):
                            raise ValueError("metadata must be in the format [metadata]")
                        metadata_dict: dict = {}
                        if metadata.startswith('[') and metadata.endswith(']'):
                            metadata: str = metadata.removesuffix(']').removeprefix('[')
                            metadata_list: list[str] = metadata.split(' ')
                            #for metadata_item in metadata_list:
                            # metadata_dict[metadata.split('=')[0]] = metadata.split('=')[1]

                            print(metadata)
                            

                        data[key] = (name, x, y, metadata_dict)
                return data

        except ValueError as e:
            print(e)

def main() -> None:

    if len(sys.argv) != 2:
        print("Usage: python map_parser.py <map_file>")
        sys.exit(1)
    else:
        parser: Parser = Parser(sys.argv[1])
        data: dict = parser.parse()
        print(data)



if __name__ == "__main__":
    main()

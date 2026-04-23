from pydantic import BaseModel, Field, model_validator, ValidationError
import sys


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
                    if striped_line != "nb_drones":
                        raise ValueError("First line must be nb_drones")
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

                    if key == "nb_drones" and key in data.keys():
                        raise ValueError("nb_drones already exists")

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

                        if metadata.startswith('[') and metadata.endswith(']'):
                            metadata.removesuffix(']')
                            metadata.removesuffix('[')
                            metadata: str = metadata.strip()
                            

                        data[key] = (name, x, y)

        except ValueError as e:
            pass

def main() -> None:

    if len(sys.argv) != 2:
        print("Usage: python map_parser.py <map_file>")
        sys.exit(1)
    else:
        parser: Parser = Parser(sys.argv[1])
        data: dict = parser.parse()



if __name__ == "__main__":
    main()

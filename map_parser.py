from pydantic import BaseModel, Field, model_validator, ValidationError
import sys


class Parser:

    def __init__(self, map: str) -> None:
        self.map: str = map

    def parse(self) -> dict:
        try:
            with open(self.map) as file:
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

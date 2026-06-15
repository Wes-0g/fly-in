from map_parser import Parser
from sys import argv, exit
from simulation import Simulator


def main() -> None:

    if len(argv) != 2:
        print("Usage: python3 map_parser.py <map_file>")
        exit(1)

    parser: Parser = Parser(map=argv[1])

    try:
        map = parser.parse()
    except (ValueError, FileNotFoundError, PermissionError) as e:
        print(f"{e}")
        exit(1)

    sim: Simulator = Simulator(map)
    sim.simulate()


if __name__ == "__main__":
    main()

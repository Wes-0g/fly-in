from map_parser import Parser
from sys import argv, exit
from simulation import Simulator


def main() -> None:
    """Main entry point for the drone simulation program.

    Parses command line arguments, loads the map file, initializes
    the simulator, and runs the simulation.

    Exits with code 1 if arguments are invalid or map parsing fails.
    """

    if len(argv) != 2:
        print("Usage: python3 map_parser.py <map_file>")
        exit(1)

    parser: Parser = Parser(map=argv[1])

    try:
        map = parser.parse()
    except (ValueError, FileNotFoundError, PermissionError) as e:
        print(f"{e}")
        exit(1)

    try:
        sim: Simulator = Simulator(map)
        sim.simulate()
    except ValueError as e:
        print(f"{e}")
        exit(1)


if __name__ == "__main__":
    main()

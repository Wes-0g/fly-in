*This project has been created as part of the 42 curriculum by zel-fati.*

# FLY-IN

## Description

**Fly-in** is a multi drone routing simulation that navigates drones from a central base to a target location through a network of connected zones, while minimizing the total number of simulation turns and respecting strict movement constraints.

### Goal

The goal is to design a system that efficiently routes all drones from a `start_hub` to an `end_hub` in the fewest possible simulation turns, while handling zone capacities, link capacities, zone types (`normal`, `restricted`, `priority`, `blocked`), and multi-turn movement mechanics for restricted zones.

### Overview

The project consists of:
- A map file parser with full validation and clear error reporting
- A graph engine built from scratch (no external graph libraries)
- A Dijkstra-based pathfinding algorithm with k-shortest path discovery
- A turn-based simulation engine with capacity enforcement
- A colored terminal output system for visual feedback

## Instructions

### Installation

```bash
make install
```

### Execution

```bash
make run map=<path_to_map_file>
```

Or manually:

```bash
python3 fly-in.py <path_to_map_file>
```

### Debug Mode

```bash
make debug map=<path_to_map_file>
```

### Code Quality

```bash
make lint
```

### Clean

```bash
make clean
```

### Example

**Input map:**

```
nb_drones: 5

start_hub: hub 0 0 [color=green]
end_hub: goal 10 10 [color=yellow]
hub: roof1 3 4 [zone=restricted color=red]
hub: roof2 6 2 [zone=normal color=blue]
hub: corridorA 4 3 [zone=priority color=green max_drones=2]
hub: tunnelB 7 4 [zone=normal color=red]
hub: obstacleX 5 5 [zone=blocked color=gray]

connection: hub-roof1
connection: hub-corridorA
connection: roof1-roof2
connection: roof2-goal
connection: corridorA-tunnelB [max_link_capacity=2]
connection: tunnelB-goal
```

**Output:**

```
[T1] D1-corridorA D2-hub-roof1
[T2] D1-tunnelB D2-roof1 D3-corridorA
[T3] D1-goal D2-roof2 D3-tunnelB D4-hub-roof1 D5-corridorA
[T4] D2-goal D3-goal D4-roof1 D5-tunnelB
[T5] D4-roof2 D5-goal
[T6] D4-goal
```


## Algorithm Choices and Implementation Strategy

### Graph

The graph is implemented from scratch as an adjacency list — a `dict[str, list[tuple[str, Connection]]]` — without any external graph library. It supports neighbor queries, connection lookups, and zone retrieval by name.

### Pathfinding — Dijkstra with Priority Preference

A weighted Dijkstra algorithm is used, where movement cost is determined by the destination zone type. The priority queue stores `(cost, is_priority, zone_name)` tuples — equal-cost paths prefer priority zones by using `0` for priority zones and `1` for others as a tie-breaker in the min-heap.

Blocked zones are filtered out before being enqueued. Restricted zones add 2 to the cost.

**Complexity:** `O((V + E) log V)` per Dijkstra call, where V = zones and E = connections.

### K-Shortest Paths — Penalty-Based Approach

To distribute drones across multiple routes, a penalty-based k-shortest path algorithm is used. After finding the first path, intermediate zones are penalized with a low cost (`+0.5`) and Dijkstra is re-run to find alternative routes. This avoids hard blocking while still discouraging path reuse, and handles graphs where only one path exists.

Paths are deduplicated using `tuple[str, ...]` zone name keys stored in a `set`.


### Simulation Engine

The simulation runs in discrete turns. Each turn:

1. Link occupancy is reset (except connections held by in-transit drones)
2. All active drone states reset to `WAITING`
3. In-transit drones are processed first (forced arrival at restricted zone)
4. Active drones attempt to move (capacity checks on zone and link)
5. Waiting drones attempt to enter the network
6. Movements are applied and output is printed

**Restricted zone mechanic:** When a drone commits to a restricted zone, it occupies the connection for turn 1 (output: `D1-zoneA-zoneB`) and must arrive on turn 2 (output: `D1-zoneB`). The destination zone is reserved immediately on turn 1 to prevent conflicts.

**Capacity rules enforced:**
- `zones_occupation[zone] < zone.max_drones` before entering any zone
- `links_occupation[edge] < conn.max_link_capacity` before traversing any connection
- Start and end zones are uncapped

**Drone ordering:** At the beginning of each turn, drones are sorted in ascending order by their IDs. This guarantees a consistent and predictable movement sequence across simulations, with lower-ID drones moving first to minimize movement conflicts and blocking issues.


## Visual Representation

Terminal output uses raw ANSI escape codes — no external color libraries. Each zone name in the simulation output is colorized using the `color` attribute defined in the map file.

```
[T1] D1-corridorA D2-hub-roof1
[T2] D1-tunnelB D2-roof1 D3-corridorA
[T3] D1-goal D2-roof2 D3-tunnelB
```

- Zone names are colorized with their map-defined color (e.g., `red`, `green`, `blue`)
- Drone identifiers (`D1`, `D2`) remain plain white for readability
- Restricted transit connections show both zone names colorized independently: `D1-zoneA-zoneB`
- Turn numbers are prefixed in brackets: `[T1]`

This makes it immediately clear which zones drones are moving through, which paths are being used simultaneously, and where bottlenecks occur.

## Project Structure

```
.
├── fly-in.py            # Entry point, argument parsing
├── map_parser.py        # Map file parser
├── models.py            # Pydantic models
├── drone_network.py     # Graph class and Dijkstra / k-shortest paths
├── drone.py             # Drone class and DroneState enum
├── simulator.py         # Turn-based simulation engine
├── colorize.py          # ANSI terminal color utilities
├── Makefile
├── requirements.txt
├── .gitignore
└── README.md
```


## Resources

### Documentation and References

- [Dijkstra's Algorithm - GeeksforGeeks](https://www.geeksforgeeks.org/dsa/dijkstras-shortest-path-algorithm-greedy-algo-7/)
- [Graph Data Structure - GeeksforGeeks](https://www.geeksforgeeks.org/dsa/graph-data-structure/)
- [heapq — Heap queue algorithm - Python docs](https://docs.python.org/3/library/heapq.html)

### AI Usage

AI tools were used in this project specifically for:
- **Understanding Dijkstra's algorithm:** Used AI to understand how Dijkstra works step by step — how the priority queue is used, how costs are updated, and how the shortest path is reconstructed from the visited nodes. The implementation was then written and understood independently.
- **Docstrings and documentation:** AI was used to generate first drafts of docstrings for functions and classes following PEP 257 / Google style. Each docstring was reviewed, corrected, and adapted to match the actual implementation.
- **Test design:** AI helped generate test cases for the map parser, covering edge cases from the subject requirements. All tests were reviewed and run manually to confirm they reflect actual parser behavior.

from enum import Enum
from map_parser import Zone


class DroneState(Enum):
    WAITING = "waiting"
    MOVING = "moving"
    ARRIVED = "arrived"


class Drone:

    def __init__(self, id: int, current_zone: str) -> None:
        self.id = id
        self.current_zone = current_zone
        self.path: list[Zone] = []
        self.path_index: int = 0
        self.state: DroneState = DroneState.WAITING

    def current_zone(self) -> Zone:
        return self.path[self.path_index]

    def next_zone(self) -> Zone | None:
        if self.arrived():
            return None
        return self.path[self.path_index + 1]

    def arrived(self) -> bool:
        return self.path_index == len(self.path) - 1

from enum import Enum
from models import Zone
from colorize import colorize


class DroneState(Enum):
    WAITING = "waiting"
    MOVING = "moving"
    ARRIVED = "arrived"


class Drone:

    def __init__(self, id: int, path: list[Zone]) -> None:
        self.id: int = id
        self.path: list[Zone] = path
        self.path_index: int = 0
        self.state: DroneState = DroneState.WAITING
        self.is_restricted: bool = False

    @property
    def current_zone(self) -> Zone:
        return self.path[self.path_index]

    @property
    def next_zone(self) -> Zone | None:
        if self.arrived:
            return None
        return self.path[self.path_index + 1]

    @property
    def arrived(self) -> bool:
        return self.path_index == len(self.path) - 1

    @property
    def current_connection(self) -> tuple[str, str]:

        return (colorize(self.path[self.path_index].name,
                         self.path[self.path_index].color),
                colorize(self.path[self.path_index + 1].name,
                         self.path[self.path_index + 1].color))

    def move(self) -> None:
        if not self.arrived:
            self.path_index += 1

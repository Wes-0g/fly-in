from enum import Enum
from map_parser import Zone


class DroneState(Enum):
    WAITING = "waiting"
    MOVING = "moving"
    IN_THE_WAY = "in_the_way"
    ARRIVED = "arrived"


class Drone:

    def __init__(self, id: int, path: list[Zone]) -> None:
        self.id: int = id
        self.path: list[Zone] = path
        self.path_index: int = 0
        self.state: DroneState = DroneState.WAITING
        self.turns_in_restricted: int = 0
        self.restricted_zone: str | None = None

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
        return (self.path[self.path_index].name,
                self.path[self.path_index + 1].name)

    def move(self) -> None:
        if self.state == DroneState.IN_THE_WAY:
            self.turns_in_restricted -= 1
            if self.turns_in_restricted == 0:
                self.path_index += 1
                self.restricted_zone = None

        else:
            if not self.arrived:
                self.path_index += 1

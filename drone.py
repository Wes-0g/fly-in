from enum import Enum
from map_parser import Zone


class DroneState(Enum):
    WAITING = "waiting"
    MOVING = "moving"
    IN_TRANSIT = "in_transit"
    ARRIVED = "arrived"


class Drone:

    def __init__(self, id: int, current_zone: str) -> None:
        self.id = id
        self.current_zone = current_zone
        self.path: list[Zone] = []
        self.path_index: int = 0
        self.state: DroneState = DroneState.WAITING
        #self.turns_in_transit: int = 0
        #self.transit_target: str | None = None

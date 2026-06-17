from enum import Enum
from models import Zone
from colorize import colorize


class DroneState(Enum):
    """Enumeration of possible drone states.

    Attributes:
        WAITING: Drone is waiting to start moving.
        MOVING: Drone is currently moving through the network.
        ARRIVED: Drone has reached its destination.
    """
    WAITING = "waiting"
    MOVING = "moving"
    ARRIVED = "arrived"


class Drone:
    """Represents a drone navigating through the zone network.

    Attributes:
        id: Unique identifier for the drone.
        path: List of zones representing the drone's route.
        path_index: Current position index in the path.
        state: Current state of the drone (WAITING, MOVING, ARRIVED).
        is_restricted: Whether the drone is in a restricted zone.
    """

    def __init__(self, id: int, path: list[Zone]) -> None:
        """Initialize a Drone with an ID and path.

        Args:
            id: Unique identifier for the drone.
            path: List of Zone objects representing the drone's route.
        """
        self.id: int = id
        self.path: list[Zone] = path
        self.path_index: int = 0
        self.state: DroneState = DroneState.WAITING
        self.is_restricted: bool = False

    @property
    def current_zone(self) -> Zone:
        """Get the current zone of the drone.

        Returns:
            The Zone object where the drone is currently located.
        """
        return self.path[self.path_index]

    @property
    def next_zone(self) -> Zone | None:
        """Get the next zone in the drone's path.

        Returns:
            The next Zone object, or None if the drone has arrived.
        """
        if self.arrived:
            return None
        return self.path[self.path_index + 1]

    @property
    def arrived(self) -> bool:
        """Check if the drone has reached its destination.

        Returns:
            True if the drone is at the final zone, False otherwise.
        """
        return self.path_index == len(self.path) - 1

    @property
    def current_connection(self) -> tuple[str, str]:
        """Get the current connection as a tuple of colored zone names.

        Returns:
            Tuple of (current_zone_name, next_zone_name) with color formatting.
        """

        return (colorize(self.path[self.path_index].name,
                         self.path[self.path_index].color),
                colorize(self.path[self.path_index + 1].name,
                         self.path[self.path_index + 1].color))

    def move(self) -> None:
        """Move the drone to the next zone in its path.

        Increments the path index if the drone has not arrived
        and is not in a restricted zone.
        """
        if not self.arrived and not self.is_restricted:
            self.path_index += 1

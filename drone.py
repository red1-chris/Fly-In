from __future__ import annotations
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from hub import Hub
    from connection import Connection


class Drone:
    def __init__(self, drone_id: int, start_hub: Hub) -> None:
        """Initialize a drone at its starting hub"""
        self.id = drone_id
        self.current_hub: Hub = start_hub
        self.prev_hub: Hub = start_hub
        self.path: List[Hub] = []
        self.is_arrived: bool = False
        self.wait_turns: int = 0
        self.in_transit: bool = False
        self.just_arrived: bool = False

    def move_to(self, next_hub: Hub, connection: Connection) -> str:
        """Move the drone to next_hub via connection and return output string

                Sets wait_turns based on hub cost. Sets in_transit=True if the
        destination is restricted (cost > 1).

        Args:
            next_hub: The hub to move into.
            connection: The connection used for this move.

        Returns:
            Movement string in format D<id>-<hub> or D<id>-<conn>.
        """

        if self in self.current_hub.drones:
            self.current_hub.drones.remove(self)
        self.prev_hub = self.current_hub
        self.current_hub = next_hub
        self.current_hub.drones.append(self)
        # initiating restricted hub reactions
        self.wait_turns = next_hub.cost - 1
        if self.wait_turns > 0:
            self.in_transit = True
            return (
                f"D{self.id}-{connection.zones[0].name}"
                f"-{connection.zones[1].name}"
            )
        else:
            return f"D{self.id}-{next_hub.name}"

    def can_move(self) -> bool:
        """Return True if the drone is ready to move this turn

        A drone cannot move if it is still waiting (wait_turns > 0)
        or if it is just arrived on a restricted hub this turn"""
        return self.wait_turns <= 0 and not self.just_arrived

    def update_wait(self) -> None:
        """Decrement wait counter and update transit/arrival flags"""
        self.just_arrived = False
        if self.wait_turns > 0:
            self.wait_turns -= 1
            if self.wait_turns == 0:
                self.in_transit = False
                self.just_arrived = True
                self.prev_hub = self.current_hub
        else:
            self.in_transit = False

    def __repr__(self) -> str:
        """Return a string representation of the drone"""
        return (f"Drone(id={self.id}, pos={self.current_hub.name},"
                f"wait={self.wait_turns})")

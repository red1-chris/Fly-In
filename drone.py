from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from hub import Hub


class Drone:
    def __init__(self, drone_id: int, start_hub: Hub) -> None:
        self.id = drone_id
        self.current_hub: Hub = start_hub
        self.path: List[Hub] = []
        self.is_arrived: bool = False
        self.wait_turns: int = 0

    def move_to(self, next_hub: Hub) -> str:
        if self in self.current_hub.drones:
            self.current_hub.drones.remove(self)
        self.current_hub = next_hub
        self.current_hub.drones.append(self)
        self.wait_turns = next_hub.cost - 1
        return f"D{self.id}-{next_hub.name}"

    def can_move(self) -> bool:
        return self.wait_turns <= 0

    def update_wait(self) -> None:
        if self.wait_turns > 0:
            self.wait_turns -= 1

    def __repr__(self) -> str:
        return (f"Drone(id={self.id}, pos={self.current_hub.name},"
                f"wait={self.wait_turns})")

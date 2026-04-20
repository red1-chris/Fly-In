from __future__ import annotations
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from drone import Drone


class Hub:
    def __init__(
            self,
            name: str,
            x: int,
            y: int,
            zone_type: str = 'normal',
            max_drones: int = 1,
            color: str = "none"
            ) -> None:
        self.name = name
        self.x = x
        self.y = y
        self.type = zone_type
        self.max_drones = max_drones
        self.color = color
        self.cost = 1
        self.drones: list[Drone] = []

    def can_add_drone(self) -> bool:
        return len(self.drones) < self.max_drones

    def __repr__(self):
        return (f"Hub(name='{self.name}', type='{self.type}', "
                f"drones={len(self.drones)}/{self.max_drones})")


class RestrictedHub(Hub):
    def __init__(
            self,
            name: str,
            x: int,
            y: int,
            max_drones: int = 1,
            color: str = "none"
            ) -> None:
        super().__init__(name, x, y, 'restricted', max_drones, color)
        self.cost = 2


class PriorityHub(Hub):
    def __init__(
            self,
            name: str,
            x: int,
            y: int,
            max_drones: int = 1,
            color: str = "none"
            ) -> None:
        super().__init__(name, x, y, 'priority', max_drones, color)
        self.cost = 1


class BlockedHub(Hub):
    def __init__(
            self,
            name: str,
            x: int,
            y: int,
            max_drones: int = 0,
            color: str = "none"
            ) -> None:
        super().__init__(name, x, y, 'blocked', max_drones, color)


class HubFactory:
    @staticmethod
    def create(h_type: str, name: str, x: int, y: int, meta: dict) -> Hub:
        zone = meta.get("zone", "normal")
        if h_type in ["start_hub", "end_hub"]:
            zone = h_type

        max_d = int(meta.get("max_drones", 0 if h_type == "blocked" else 1))
        color = meta.get("color", "none")

        if zone == "restricted":
            return RestrictedHub(name, x, y, max_d, color)
        elif zone == "priority":
            return PriorityHub(name, x, y, max_d, color)
        elif zone == "blocked":
            return BlockedHub(name, x, y, max_d, color)
        else:
            return Hub(name, x, y, "normal", max_d, color)

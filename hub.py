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
        from .drone import Drone
        self.drones: list[Drone] = []

    def can_add_drone(self) -> bool:
        return len(self.drones) <= self.max_drones


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

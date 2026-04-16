from .hub import Hub


class Connection:
    def __init__(self, zone_a: Hub, zone_b: Hub, max_link_capacity: int = 1):
        self.zones = (zone_a, zone_b)
        self.max_link_capacity = max_link_capacity
        self.current_traffic = 0

    def is_full(self) -> bool:
        return self.current_traffic >= self.max_link_capacity

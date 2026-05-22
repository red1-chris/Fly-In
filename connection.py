from hub import Hub


class Connection:

    def __init__(self, zone_a: Hub, zone_b: Hub, max_link_capacity: int = 1):
        """Initialize a connection between two hubs"""
        self.zones = (zone_a, zone_b)
        self.max_link_capacity = max_link_capacity
        self.current_traffic = 0

    def is_full(self) -> bool:
        """Return True if the connection has reached its traffic capacity"""
        return self.current_traffic >= self.max_link_capacity

    def add_traffic(self) -> None:
        """Increment current traffic by one, raising an error if full"""
        if self.is_full():
            raise ValueError("Connection is at full capacity")
        self.current_traffic += 1

    def reset_traffic(self) -> None:
        """Reset current traffic to zero at the start of each turn"""
        self.current_traffic = 0

    def get_destination(self, origin: Hub) -> Hub:
        """Return the hub at the other end of the connection from origin"""
        return self.zones[1] if self.zones[0] == origin else self.zones[0]

    def __repr__(self) -> str:
        """Return a string representation of the connection"""
        return (f"Link({self.zones[0].name}<->{self.zones[1].name},"
                f" cap={self.max_link_capacity})")

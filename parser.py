from hub import Hub, HubFactory
from connection import Connection
import re
from typing import List, Dict, Optional, Set, Tuple


class Parser:

    HUB_PATTERN = (
        r"^(hub|start_hub|end_hub):\s+"
        r"([^\s-]+)\s+(-?\d+)\s+(-?\d+)(?:\s+\[(.*)\])?$"
    )
    CONN_PATTERN = r"^connection:\s+([^\s-]+)-([^\s-]+)(?:\s+\[(.*)\])?$"
    DRONE_PATTERN = r"^nb_drones:\s+(\d+)$"
    VALID_ZONE_TYPES = {"normal", "restricted", "priority", "blocked"}

    def __init__(self, file_path: str) -> None:
        """Initialize the parser with the path to a map file"""
        self.file_path = file_path
        self.nb_drones: int = 0
        self.hubs: Dict[str, Hub] = {}
        self.connections: List[Connection] = []
        self.start_hub: Optional[Hub] = None
        self.end_hub: Optional[Hub] = None
        self._conn_pairs: Set[Tuple[str, str]] = set()

    def parse_metadata(self, raw_meta: str | None) -> Dict[str, str]:
        """Parse bracketes metadata into a key-value dict."""
        if not raw_meta:
            return {}
        try:
            return dict(item.split("=") for item in raw_meta.split()
                        if "=" in item)
        except ValueError:
            return {}

    def load(self) -> None:
        """Load and parse the map file, raising errors on invalid input."""
        with open(self.file_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                # nb_drones test
                drone_match = re.match(self.DRONE_PATTERN, line)
                if drone_match:
                    self.nb_drones = int(drone_match.group(1))
                    if self.nb_drones <= 0:
                        raise ValueError(
                            f"Line {line_num}: nb_drones must be a positive"
                            f"integer, got {self.nb_drones}"
                        )
                    continue
                # hub test
                hub_match = re.match(self.HUB_PATTERN, line)
                if hub_match:
                    self._create_hub(hub_match, line_num)
                    continue
                # connection test:
                conn_match = re.match(self.CONN_PATTERN, line)
                if conn_match:
                    self._create_connection(conn_match, line_num)
                    continue
                # if not any, syntax error
                raise SyntaxError(
                    f"line Error {line_num}: Invalid line format: {line}"
                    )
            self._validate()

    def _validate(self) -> None:
        """Run post-load checks on the fully parsed map."""
        if self.nb_drones <= 0:
            raise ValueError(
                "Missing or invalid 'nb_drones' - must be a positive integer"
            )
        if self.start_hub is None:
            raise ValueError(
                "Missing 'start_hub' - exactly one start_hub is required"
            )
        if self.end_hub is None:
            raise ValueError(
                "Missing 'end_hub' - exactly one end_hub is required"
            )
        # Check if the graph is connected (start can reach end)
        if not self._is_reachable(self.start_hub, self.end_hub):
            raise ValueError(
                f"Graph is disconnected: no path from "
                f"'{self.start_hub.name}' to '{self.end_hub.name}'"
            )

    def _is_reachable(self, start: Hub, end: Hub) -> bool:
        """BFS to check wether end is reachable from start."""
        visited: Set[Hub] = set()
        queue = [start]
        while queue:
            current = queue.pop(0)
            if current == end:
                return True
            if current in visited:
                continue
            visited.add(current)
            for link in current.links:
                neighbour = link.get_destination(current)
                if neighbour.type != 'blocked' and neighbour not in visited:
                    queue.append(neighbour)
        return False

    def _create_hub(self, match: re.Match, line_num: int) -> None:
        """Parse and validate a hub line, then register it."""
        h_type = match.group(1)
        name = match.group(2)
        x, y = int(match.group(3)), int(match.group(4))
        meta = self.parse_metadata(match.group(5))

        # Duplicate zone name
        if name in self.hubs:
            raise ValueError(
                f"Line {line_num}: duplicate zone name '{name}'"
            )

        # Only one start_hub and one end_hub allowed
        if h_type == "start_hub" and self.start_hub is not None:
            raise ValueError(
                f"Line {line_num}: Multiple start_hub definitions found"
            )
        if h_type == "end_hub" and self.end_hub is not None:
            raise ValueError(
                f"Line {line_num}: Multiple end_hub definitions found"
            )
        # Validate zone type
        zone = meta.get("zone", "normal")
        if h_type not in ("start_hub", "end_hub"):
            if zone not in self.VALID_ZONE_TYPES:
                raise ValueError(
                    f"Line {line_num}: Invalid zone type '{zone}' for hub "
                    f"'{name}'. Must be one of: "
                    f"{', '.join(self.VALID_ZONE_TYPES)}"
                )
        # Validate max_drones
        if "max_drones" in meta:
            try:
                max_d = int(meta["max_drones"])
            except ValueError:
                raise ValueError(
                    f"Line {line_num}: max_drones must be an integer "
                    f"for hub '{name}', got '{meta['max_drones']}'"
                )
            if h_type != "blocked" and max_d <= 0:
                raise ValueError(
                    f"Line {line_num}: max_drones must be a positive integer "
                    f"for hub '{name}', got {max_d}"
                )

        self.hubs[name] = HubFactory.create(h_type, name, x, y, meta)
        if h_type == "start_hub":
            self.start_hub = self.hubs[name]
        elif h_type == "end_hub":
            self.end_hub = self.hubs[name]
        print(f"Creating Hub: {name} of type {h_type} at ({x}, {y}) "
              f"with meta {meta}")

    def _create_connection(self, match: re.Match, line_num: int) -> None:
        """Parse and validate a connection line, then register it"""
        name_a = match.group(1)
        name_b = match.group(2)
        meta = self.parse_metadata(match.group(3))

        # Both hubs must be defined
        if name_a not in self.hubs:
            raise ValueError(
                f"Line {line_num}: Unknown zone '{name_a}' in connection"
            )
        if name_b not in self.hubs:
            raise ValueError(
                f"Line {line_num}: unknown zone '{name_b}' in connection"
            )
        # Duplicate connection check (a-b == b-a)
        pair = (min(name_a, name_b), max(name_a, name_b))
        if pair in self._conn_pairs:
            raise ValueError(
                f"Line {line_num}: Duplicate connection "
                f"'{name_a}-{name_b}' (already defined)"
            )
        self._conn_pairs.add(pair)
        # Validate max_link_capacity
        max_cap = 1
        if "max_link_capacity" in meta:
            try:
                max_cap = int(meta["max_link_capacity"])
            except ValueError:
                raise ValueError(
                    f"Line {line_num}: max_link_capacity must be an integer "
                    f"for connection '{name_a}-{name_b}', "
                    f"got '{meta['max_link_capacity']}'"
                )
            if max_cap <= 0:
                raise ValueError(
                    f"Line {line_num}: max_link_capacity must be a positive "
                    f"integer for connection '{name_a}-{name_b}',"
                    f" got {max_cap}"
                )

        hub_a = self.hubs[name_a]
        hub_b = self.hubs[name_b]
        new_conn = Connection(hub_a, hub_b, max_cap)
        self.connections.append(new_conn)
        hub_a.links.append(new_conn)
        hub_b.links.append(new_conn)
        print(f"Creating Connection: {name_a} <-> {name_b} with meta {meta}")

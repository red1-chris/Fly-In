from hub import Hub, HubFactory
from connection import Connection
import re
from typing import List, Dict


class Parser:

    HUB_PATTERN = (
        r"^(hub|start_hub|end_hub):\s+"
        r"([^\s-]+)\s+(-?\d+)\s+(-?\d+)(?:\s+\[(.*)\])?$"
    )
    CONN_PATTERN = r"^connection:\s+([^\s-]+)-([^\s-]+)(?:\s+\[(.*)\])?$"
    DRONE_PATTERN = r"^nb_drones:\s+(\d+)$"

    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        self.nb_drones: int = 0
        self.hubs: Dict[str, Hub] = {}
        self.connections: List[Connection] = []
        self.start_hub: Hub = None
        self.end_hub: Hub = None

    def parse_metadata(self, raw_meta: str | None) -> Dict[str, str]:
        if not raw_meta:
            return {}
        try:
            return dict(item.split("=") for item in raw_meta.split()
                        if "=" in item)
        except ValueError:
            return {}

    def load(self) -> None:
        with open(self.file_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                # nb_drones test
                drone_match = re.match(self.DRONE_PATTERN, line)
                if drone_match:
                    self.nb_drones = int(drone_match.group(1))
                    continue
                # hub test
                hub_match = re.match(self.HUB_PATTERN, line)
                if hub_match:
                    self._create_hub(hub_match)
                    continue
                # connection test:
                conn_match = re.match(self.CONN_PATTERN, line)
                if conn_match:
                    self._create_connection(conn_match)
                    continue
                # if not any, syntax error
                raise SyntaxError(f"line Error {line_num}:"
                                  f" Invalid line format: {line}")

    def _create_hub(self, match: re.Match) -> None:
        h_type = match.group(1)
        name = match.group(2)
        x, y = int(match.group(3)), int(match.group(4))
        meta = self.parse_metadata(match.group(5))
        self.hubs[name] = HubFactory.create(h_type, name, x, y, meta)
        if h_type == "start_hub":
            self.start_hub = self.hubs[name]
        elif h_type == "end_hub":
            self.end_hub = self.hubs[name]
        print(f"Creating Hub: {name} of type {h_type} at ({x}, {y}) "
              f"with meta {meta}")

    def _create_connection(self, match: re.Match) -> None:
        name_a = match.group(1)
        name_b = match.group(2)
        meta = self.parse_metadata(match.group(3))
        if name_a not in self.hubs or name_b not in self.hubs:
            raise ValueError(f"Connection Error: {name_a} or {name_b} "
                             "not defined")
        hub_a = self.hubs[name_a]
        hub_b = self.hubs[name_b]
        new_conn = Connection(hub_a, hub_b)
        self.connections.append(new_conn)
        hub_a.links.append(new_conn)
        hub_b.links.append(new_conn)
        print(f"Creating Connection: {name_a} <-> {name_b} with meta {meta}")

from parser import Parser
from drone import Drone
from pathfinder import Pathfinder
from hub import Hub
from connection import Connection
from typing import List, Optional, Dict, TypedDict


class PathInfo(TypedDict):
    """Typed structure for path assignement data."""
    path: List[Hub]
    cost: int
    assigned: int


class Simulation:
    def __init__(self, parser: Parser) -> None:
        """Initialize the simulation from a parsed map.

        Finds multiple paths and distributes drones across them
        based on connection capacities, so they don't all follow
        the same route and block each other.

        Args:
            parser: A loaded Parser instance.
        """

        if parser.start_hub is None or parser.end_hub is None:
            raise ValueError(
                "Parser error: start_hub "
                "or end_hub is missing from the map file"
                )
        self.hubs = parser.hubs
        self.connections = parser.connections
        self.start_hub = parser.start_hub
        self.end_hub = parser.end_hub
        self.drones = [Drone(i, self.start_hub)
                       for i in range(parser.nb_drones)]
        for d in self.drones:
            self.start_hub.drones.append(d)
        self.pathfinder = Pathfinder()

        # Find up to nb_drones distinct paths so each drone can patentially
        # take a different route
        nb = parser.nb_drones
        all_paths = self.pathfinder.k_shortest_paths(
            self.start_hub, self.end_hub, k=max(nb, 3)
        )

        if not all_paths:
            raise ValueError("No path found between start and end hub.")

        # Assign paths to drones: distribute them across available paths
        # based on each path's bottleneck capacity.
        self._assign_paths(all_paths)

    def _get_path_capacity(self, path: List[Hub]) -> int:
        """Return the bottleneck capacity of a path (min connection capacity).

        Args:
            path: Ordered list of hubs.

        Returns:
            The minimum max_link_capacity among all connections on the path.
        """
        min_cap = float('inf')
        for i in range(len(path) - 1):
            conn = self.get_connection_between(path[i], path[i + 1])
            if conn is not None:
                min_cap = min(min_cap, conn.max_link_capacity)
        return int(min_cap) if min_cap != float('inf') else 1

    def _get_path_cost(self, path: List[Hub]) -> int:
        """Return total turn cost including restricted stops.

        Restricted hubs cost 2 turns (1 transit + 1 wait on hub).
        All others cost 1 turn.
        """
        cost = 0
        for hub in path[1:]:
            cost += 2 if hub.type == 'restricted' else 1
        return cost

    def _assign_paths(self, all_paths: List[List[Hub]]) -> None:
        """Distribute drones across paths prioritizing lowest cost.

        Sorts paths by total turn cost, penalizing restricted hubs
        at 2 turns each. Drones pipeline on the cheapest path first.

        Args:
            all_paths: List of candidate paths from start to end.
        """
        path_info: List[PathInfo] = []
        for p in all_paths:
            cost = self._get_path_cost(p)
            path_info.append(PathInfo(
                path=p[1:],
                cost=cost,
                assigned=0,
            ))

        path_info.sort(key=lambda x: x['cost'])

        for drone in self.drones:
            best = min(
                path_info,
                key=lambda x: (x['cost'], x['assigned'])
            )
            drone.path = list(best['path'])
            cap = self._get_path_capacity(best['path'])
            drone.wait_turns = best['assigned'] // cap
            best['assigned'] += 1

    def get_connection_between(
            self,
            h1: Hub,
            h2: Hub
            ) -> Optional[Connection]:
        """Return the connection between two adjacent hubs, or None.

        Args:
            h1: First hub.
            h2: Second hub.

        Returns:
            The Connection object if it exists, otherwise None.
        """

        for conn in h1.links:
            if h2 in conn.zones:
                return conn
        return None

    def capacity_info(self) -> List[str]:
        """Return current capacity usage for all hubs and connections.

        Called each turn when --capacity-info flag is active.

        Returns:
            List of strings describing current capacity state.
        """
        lines = []
        lines.append("  [Hubs]")
        for name, hub in self.hubs.items():
            count = len(hub.drones)
            if count > 0 or hub.max_drones < 99:
                lines.append(
                    f"  {name}: {count}/{hub.max_drones} drones"
                    + (" [FULL]" if count >= hub.max_drones else "")
                    )
        lines.append("  [Connections]")
        for conn in self.connections:
            a, b = conn.zones
            traffic = conn.current_traffic
            cap = conn.max_link_capacity
            if cap > 1 or traffic > 0:
                lines.append(
                    f"  {a.name}<->{b.name}: {traffic}/{cap}"
                    + (" [FULL]" if conn.is_full() else "")
                    )
        return lines

    def next_step(self) -> List[str]:
        """Advance the simulation by one turn.

        All connections are reset, wait counters decremented, then each
        drone that can move attempts to do so. Drones that cannot move
        (blocked hub, full connection, still waiting) stay in place.

        Returns:
            List of movement strings for this turn (e.g. ["D0-roof1"]).
        """

        moves: List[str] = []

        for conn in self.connections:
            conn.reset_traffic()

        for drone in self.drones:
            drone.update_wait()

        # Track how many drones are moving into each hub this turn,
        # so we respect capacity even when multiple drones move simultaneously.
        incoming: Dict[Hub, int] = {}
        outgoing: Dict[Hub, int] = {}

        for drone in self.drones:
            if drone.is_arrived:
                continue
            if not drone.path:
                if drone.current_hub == self.end_hub:
                    drone.is_arrived = True
                continue
            if not drone.can_move():
                continue

            target_hub = drone.path[0]
            link = self.get_connection_between(drone.current_hub, target_hub)

            if self.can_move_drone(drone, target_hub, incoming, outgoing, link):
                incoming[target_hub] = incoming.get(target_hub, 0) + 1
                outgoing[drone.current_hub] = outgoing.get(drone.current_hub, 0) + 1
                if link is None:
                    continue
                move_msg = drone.move_to(target_hub, link)
                moves.append(move_msg)
                drone.path.pop(0)
                if target_hub == self.end_hub:
                    drone.is_arrived = True
                    drone.prev_hub = drone.current_hub

        return moves

    def can_move_drone(
            self,
            drone: Drone,
            target_hub: Hub,
            incoming: Dict[Hub, int],
            outgoing: Dict[Hub, int],
            conn: Optional[Connection]
            ) -> bool:
        """Check whether a drone can legally move to target_hub this turn.

        Takes into account zone capacity (including drones already moving
        out this turn), connection capacity, and blocked zones.

        Args:
            drone: The drone trying to move.
            target_hub: The hub it wants to enter.
            incoming: Dict tracking how many drones are already moving
                      into each hub this turn.
            conn: The connection between current and target hub.

        Returns:
            True if the move is legal and resources are reserved.
        """

        if target_hub.type == 'blocked':
            return False

        # Check connection capacity
        if conn is not None and conn.is_full():
            return False

        # End hub accepts unlimited drones
        if target_hub == self.end_hub:
            if conn is not None:
                conn.add_traffic()
            return True

        # Count drones currently in target (minus those leaving this turn)
        current_occupancy = len(target_hub.drones)
        already_incoming = incoming.get(target_hub, 0)
        already_outgoing = outgoing.get(target_hub, 0)  # drones déjà validés comme partants
        effective_occupancy = current_occupancy - already_outgoing + already_incoming

        if effective_occupancy >= target_hub.max_drones:
            return False

        if conn is not None:
            conn.add_traffic()

        return True

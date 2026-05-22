import heapq
# provides heap (priority queue) algorithm on regular Ptyhon lists.
from typing import Dict, List, Optional, Set
from hub import Hub


class Pathfinder:
    @staticmethod
    def dijkstra(start_hub: Hub,
                 blocked: Optional[Set[Hub]] = None
                 ) -> Dict[Hub, Optional[Hub]]:
        """Find shortest paths from start_hub using Dijkstra's algorithm.

        Args:
            start_hub: The hub to start from.
            blocked: Optional set of hubs to treat as inaccessible.

        Returns:
            A dict mapping each hub to its parent in the shortest path tree.
        """
        if blocked is None:
            blocked = set()
        # distance[hub] = min time to reach hub from start_hub
        distances: Dict[Hub, float] = {start_hub: 0.0}
        # parents[hub] = previous hub in quickest path from start_hub
        parents: Dict[Hub, Optional[Hub]] = {start_hub: None}
        # priority_queue contains tuples (distance, hub)
        pq = [(0.0, start_hub)]
        while pq:
            # headpop() pops the smallest item off the heap
            current_dist, current_hub = heapq.heappop(pq)
            if current_dist > distances.get(current_hub, float('inf')):
                continue
            for link in current_hub.links:
                neighbour = link.get_destination(current_hub)
                if neighbour.type == 'blocked':
                    continue
                if neighbour in blocked:
                    continue
                if neighbour.type == 'priority':
                    step_cost = neighbour.cost - 0.001
                else:
                    step_cost = float(neighbour.cost)

                new_dist = current_dist + step_cost
                if new_dist < distances.get(neighbour, float('inf')):
                    distances[neighbour] = new_dist
                    parents[neighbour] = current_hub
                    # heappush(): Push item onto heap while
                    # maintaining the heap invariant.
                    heapq.heappush(pq, (new_dist, neighbour))
        return parents

    @staticmethod
    def get_path(
        parents: Dict[Hub, Optional[Hub]],
        end_hub: Hub
    ) -> List[Hub]:
        """Reconstruct the path from the parents dict to end_hub.

        Args:
            parents: The parent mapping returned by dijkstra().
            end_hub: The destination hub.

        Returns:
            Ordered list of hubs from start to end, empty if unreachable.
        """
        if end_hub not in parents:
            return []
        path = []
        step: Optional[Hub] = end_hub
        while step is not None:
            path.append(step)
            step = parents.get(step)
        return path[::-1]  # reverse to get path from start to end

    @staticmethod
    def k_shortest_paths(
        start_hub: Hub,
        end_hub: Hub,
        k: int
    ) -> List[List[Hub]]:
        """Find up to k distinct shortest paths from start_hub to end_hub.

        Uses a spur-node approach: each new path is found by progressively
        blocking intermediate hubs from previously found paths, forcing
        Dijkstra to explore alternative routes.

        Args:
            start_hub: The starting hub.
            end_hub: The destination hub.
            k: Maximum number of paths to find.

        Returns:
            A list of paths (each path is a list of hubs, start included).
        """
        # Find the first (shortest) path
        parents = Pathfinder.dijkstra(start_hub)
        first_path = Pathfinder.get_path(parents, end_hub)
        if not first_path:
            return []

        paths: List[List[Hub]] = [first_path]
        # Hubs we've already used as spur points t oavoid redundant searches
        tried_blocked: List[Set[Hub]] = [set()]

        while len(paths) < k:
            found_new = False
            last_path = paths[-1]

            # Try blocking each intermediate hub of the last found path
            # to force a detour through a different route
            for i in range(1, len(last_path) - 1):
                # Build a blocked set: all intermediate hubs already on
                # known paths up to this spur point, except start/end
                blocked: Set[Hub] = set()
                for existing_path in paths:
                    # Block the hub right after the same prefix in each path
                    if (
                        len(existing_path) > i
                        and existing_path[:i] == last_path[:i]
                    ):
                        next_on_existing = existing_path[i]
                        if (
                            next_on_existing != end_hub
                            and next_on_existing != start_hub
                        ):
                            blocked.add(next_on_existing)
                # Also block all prefix hubs to avoid going back
                for h in last_path[1:i]:
                    blocked.add(h)
                blocked.add(start_hub)

                # Skip if we already tried this exact blocked set
                if blocked in tried_blocked:
                    continue
                tried_blocked.append(blocked)

                alt_parents = Pathfinder.dijkstra(
                    last_path[i - 1], blocked=blocked
                )
                suffix = Pathfinder.get_path(alt_parents, end_hub)

                if not suffix or len(suffix) < 2:
                    continue

                # The new candidate path = prefix up to spur + new suffix
                new_path = last_path[:i] + suffix[1:]

                # reject duplicates
                if new_path not in paths:
                    paths.append(new_path)
                    found_new = True
                    break

            if not found_new:
                break

        return paths

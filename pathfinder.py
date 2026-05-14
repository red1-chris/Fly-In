import heapq
# provides heap (priority queue) algorithm on regular Ptyhon lists.
from typing import Dict, List, Optional
from hub import Hub


class Pathfinder:
    @staticmethod
    def dijkstra(start_hub: Hub) -> Dict[Hub, Optional[Hub]]:
        # distance[hub] = min time to reach hub from start_hub
        distances: Dict[Hub, float] = {start_hub: 0}
        # parents[hub] = previous hub in quickest path from start_hub
        parents: Dict[Hub, Optional[Hub]] = {start_hub: None}
        # priority_queue contains tuples (distance, hub)
        pq = [(0, start_hub)]
        while pq:
            #headpop() pops the smallest item off the heap
            current_dist, current_hub = heapq.heappop(pq)
            if current_dist > distances.get(current_hub, float('inf')):
                continue
            for link in current_hub.links:
                neighbour = link.get_destination(current_hub)
                new_dist = current_dist + neighbour.cost
                if new_dist < distances.get(neighbour, float('inf')):
                    distances[neighbour] = new_dist
                    parents[neighbour] = current_hub
                    # heappush(): Push item onto heap while
                    # maintaining the heap invariant.
                    heapq.heappush(pq, (new_dist, neighbour))
        return parents

    @staticmethod
    def get_path(parents: Dict[Hub, Optional[Hub]], end_hub: Hub) -> List[Hub]:
        path = []
        step: Optional[Hub] = end_hub
        while step is not None:
            path.append(step)
            step = parents.get(step)
        return path[::-1]  # reverse to get path from start to end
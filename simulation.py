from parser import Parser
from drone import Drone
from pathfinder import Pathfinder

class Simulation:
    def __init__(self, parser: Parser):
        self.hubs = parser.hubs
        self.connections = parser.connections
        self.start_hub = parser.start_hub
        self.end_hub = parser.end_hub
        self.drones = [Drone(i, self.start_hub)
                       for i in range(parser.nb_drones)]
        for d in self.drones:
            self.start_hub.drones.append(d)
        self.pathfinder = Pathfinder()
        parents = self.pathfinder.dijkstra(self.start_hub)
        full_path = self.pathfinder.get_path(parents, self.end_hub)
        for drone in self.drones:
            drone.path = full_path[1:]

    def get_connection_between(self, h1, h2):
        for conn in h1.links:
            if h2 in conn.zones:
                return conn
        return None

    def next_step(self):
        moves = []
        for conn in self.connections:
            conn.reset_traffic()
        for drone in self.drones:
            drone.update_wait()
        for drone in self.drones:
            if drone.is_arrived:
                continue
            
            # Sécurité si le chemin est vide mais qu'il est déjà sur le goal
            if not drone.path:
                if drone.current_hub == self.end_hub:
                    drone.is_arrived = True
                continue
                
            if not drone.can_move():
                continue
                
            target_hub = drone.path[0]
            if self.can_move_drone(drone, target_hub):
                move_msg = drone.move_to(target_hub)
                moves.append(move_msg)
                drone.path.pop(0)
                if target_hub == self.end_hub:
                    drone.is_arrived = True
        return moves

    def can_move_drone(self, drone, target_hub) -> bool:
        # --- CORRECTION MAJEURE ---
        # Si la destination est le hub d'arrivée, on ignore la limite de capacité du Hub.
        # Mais on vérifie quand même que la ligne (connection) n'est pas saturée par un autre drone ce tour-ci.
        if target_hub == self.end_hub:
            conn = self.get_connection_between(drone.current_hub, target_hub)
            if conn and conn.is_full():
                return False
            if conn:
                conn.add_traffic()
            return True

        # Pour tous les autres hubs standards, on applique la règle de capacité maximale
        if not target_hub.can_add_drone():
            return False
            
        conn = self.get_connection_between(drone.current_hub, target_hub)
        if conn and conn.is_full():
            return False
        if conn:
            conn.add_traffic()
            
        return True
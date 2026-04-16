from .hub import Hub, BlockedHub, PriorityHub, RestrictedHub


HUB_CLASS_DICT = {
    "normal": Hub,
    "restricted": RestrictedHub,
    "priority": PriorityHub,
    "blocked": BlockedHub
}

class Parser:

    def __init__(self, nb_drones: int, hub: str, connection: str):
        self.nb_drones = nb_drones
        self.hub = hub
        self.connection = connection

    def read_map(self, map_file: str) -> dict:
        try:
            with open(map_file, "r") as f:
                for line in f.readlines():
                    if line[0] == 'nb_drones:':
                        self.nb_drones = line[1]
                    if line[0] == "hub:"

# aller voir Regex

# faire une fonction qui open un input nom de fichier de map et qui decoupe:
# premiere ligne = nom de la map
# deuxieme ligne = nb de drones sur la map
# saut de ligne definit partie du Hub
# premiere ligne = start point
# autre lignes = hubs
# derniere ligne = end point
# saut de ligne vers connections
# connctions entre hub definies par ligne et tuples.
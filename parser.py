from .hub import Hub, BlockedHub, PriorityHub, RestrictedHub


HUB_CLASS_DICT = {
    "normal": Hub,
    "restricted": RestrictedHub,
    "priority": PriorityHub,
    "blocked": BlockedHub
}

# faire une fonction qui open un input nom de fichier de map et qui decoupe:
# premiere ligne = nom de la map
# deuxieme ligne = nb de drones sur la map
# saut de ligne definit partie du Hub
# premiere ligne = start point
# autre lignes = hubs
# derniere ligne = end point
# saut de ligne vers connections
# connctions entre hub definies par ligne et tuples.
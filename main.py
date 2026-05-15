from simulation import Simulation
from parser import Parser
from visual import main_visual

# 1. Charger la simulation
parser = Parser("ton_fichier_map.txt")
parser.load()
sim = Simulation(parser)

# 2. Lancer l'interface
main_visual(sim)
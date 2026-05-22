_This project has been created as part_
_of the 42 curriculum by credwand_


## Description

Fly-In is a 42 project that requires reading and parsing a textual map,
then using a pathfinding algorithm to route multiple drones from a start
zone to an end zone in the fewest possible simulation turns.

The map is a graph of connected hubs. Each hub has a type (normal,
restricted, blocked, priority) and a maximum drone capacity. Connections
between hubs also have a capacity limit. The simulation moves drones
turn by turn, respecting all capacity and movement constraints, while
trying to minimize the total number of turns.

**Hub types:**
- `normal` — standard zone, costs 1 turn to enter
- `restricted` — sensitive zone, costs 2 turns to enter (1 turn on the
  connection, 1 turn stopped on the hub before moving again)
- `priority` — preferred zone, costs 1 turn but favored by pathfinding
- `blocked` — inaccessible, no drone may enter


## Algorithm

**Pathfinding: Dijkstra + k-shortest paths**

The core algorithm is Dijkstra's shortest path, implemented from scratch
using Python's `heapq` module (no graph libraries allowed). It finds the
minimum-cost path from start to end, where cost is the number of turns
to traverse each hub (1 for normal/priority, 2 for restricted).

To distribute drones across multiple routes and avoid bottlenecks, we
extend Dijkstra with a spur-node approach to find up to k distinct paths.
Each new path is found by progressively blocking intermediate hubs from
previously found paths, forcing exploration of alternative routes.

**Drone assignment: cost-sorted pipeline**

Paths are sorted by total turn cost (penalizing restricted hubs at 2
turns each). Drones are assigned to the cheapest path first, pipelining
behind each other. If multiple paths share the same cost, drones are
spread evenly between them.

**Complexity:**
- Dijkstra: O((V + E) log V) per run, where V = hubs, E = connections
- k-shortest paths: O(k × (V + E) log V)
- Per-turn simulation: O(D × E) where D = number of drones

**Capacity management:**

Each turn, the simulation tracks `incoming` drones per hub and `leaving`
drones from each hub simultaneously, so that a drone moving out frees
capacity for a drone moving in during the same turn — as required by the
subject rules.

**Example input:**

```
nb_drones: 3
start_hub: start 0 0 [color=green]
hub: junction 1 0 [color=yellow max_drones=2]
hub: path_a 2 1 [color=blue]
hub: path_b 2 -1 [color=blue]
end_hub: goal 3 0 [color=red max_drones=3]

connection: start-junction
connection: junction-path_a
connection: junction-path_b
connection: path_a-goal
connection: path_b-goal
```

**Expected output:**

```
#1
D0-junction D1-junction
#2
D0-path_a D1-path_b D2-junction
#3
D0-goal D1-goal D2-path_a
#4
D2-goal
```


## Visual Representation

The simulation uses **pygame** to display an interactive graphical
interface:

- **Hub color-coding:** start (green), end (red), normal (cyan),
  restricted (orange), blocked (grey)
- **Drone display:** drones in transit toward a restricted hub appear
  in **yellow at the midpoint of the connection** for one turn, then
  on the restricted hub the next turn — making the 2-turn cost visually
  clear
- **Auto-scaling:** the map scales and centers automatically to fit any
  topology on screen
- **Turn counter:** current turn displayed in real time; turns green
  with final count when simulation ends
- **Navigation buttons:** "Back to Menu" returns to map selection,
  "Restart" replays the current map from the beginning
- **Menu:** lists all `.txt` map files found in the `maps/` directory


## Instructions

**Installation & Setup (Makefile)**

This project uses `uv` as the package manager. From the root:

- `make install` — installs dependencies via `uv sync`
- `make run` — runs the simulation
- `make debug` — runs with Python's built-in debugger (`pdb`)
- `make clean` — removes `__pycache__`, `.mypy_cache` and other caches
- `make lint` — runs `flake8` and `mypy` for code style and type checking
- `make build` — builds the distributable package (`.whl` and `.tar.gz`)

**Running the Application**

```bash
make install
make run
```

A pygame window opens with a map selection menu. Click a map to start
the simulation. Use "Back to Menu" to return, or "Restart" to replay.

**Map files** must be placed in a `maps/` directory at the project root.
The program scans it recursively for `.txt` files.


## Resources

- https://www.w3schools.com/python/ref_module_heapq.asp
- https://docs.python.org/3/howto/regex.html
- https://pypi.org/project/pygame/
- https://www.pygame.org/docs/
- https://fr.wikipedia.org/wiki/Algorithme_de_Dijkstra
- https://www.datacamp.com/fr/tutorial/dijkstra-algorithm-in-python
- https://en.wikipedia.org/wiki/Yen%27s_algorithm

**Use of AI:**
Claude (Anthropic) was used to assist with debugging the simulation
logic, improving the path distribution algorithm, and refining the
visual representation. All generated code was reviewed, tested, and
understood before inclusion.
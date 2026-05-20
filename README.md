_This project has been created as part_
_of the 42 curriculum by credwand_


## **_Description:_**

Fly-In is a 42's project that requires to read and parse a textual map
and uses an algorithm to find the quickest path for drones to travel from the start point to the end point. We can show the drones' path by a visual representation.

**_Maps:_**

The maps are represented by a hubs and connections between those hubs.
There is a start_hub and an end_hub and named hubs between those.
Hubs can be normal, restricted, blocked or prioritary, it will bias the path of the drones.
They have a maximum capacity of drones autorised.
Drones can travel in groups but they are limited by the capacity of the connections too.
We used POO to define the different types of hub, the connections, the drones.
The informations of these objects were filled with those from the maps parsed.

**_Parser:_**

The Parser uses "regex" from Regular expressions.
Regular expressions are extremely useful in extracting information from text such as code, log files, spreadsheets, or even documents.
Those are essentially a tiny, highly specialized programming language embedded inside Python and made available through the re module.
It's a bit long to explain but it looks like that:
r"^(hub|start_hub|end_hub):\s+([^\s-]+)\s+(-?\d+)\s+(-?\d+)(?:\s+\[(.*)\])?$"
^ is "start of string"
$ is "end of string"
\s+ is "multiple whitespaces" etc...

So with regex, we exfiltrate the informations from the map file and distribute them in the different objects.
We can parse metadatas too like color of the hub.

**_Algorithm:_**

Once we have our objects we can interact with them and throw an algorithm that will permit us to find the quickest path from start_hub to end_hub.
In graph theory, the Dijkstra algorithm (pronounced [dɛɪkstra]) is used to solve the problem of the shortest path. It allows, for example, to determine a shorter path to get from one city to another knowing the road network of a region. More precisely, in a graph oriented weighted by positive reals G = ( S , A ), it calculates shorter paths from one source to all the other vertices. It can also be used to calculate a shorter path between a starting peak and an arrival peak.
It seemed pertinent for the task of the subject.
We used the heapq module.
The heapq module doesn't create a new object type; instead, it provides functions (heappush and heappop) that manipulate a regular Python list while maintaining a binary heap structure behind the scenes.
You initialize your priority queue (pq) as a list containing a tuple. The tuple is structured as (distance, hub).
heappop() automatically extracts the tuple with the lowest current_dist from the list.
Whenever the algorithm finds a shorter path to a neighboring hub, it pushes a new (new_dist, neighbour) tuple into the heap using heappush().
This work is done in the pathfinder.py file and applied in the objects in simulation.py

**_Visual:_**

Finally we used *_pygame_* to show a visual representation of the project.
Pygame is a cross-platform set of Python modules designed for writing video games and multimedia applications. It provides low-level graphics and audio libraries, allowing developers to manage windows, capture real-time keyboard/mouse events, and draw shapes directly onto a pixel grid.

In this project, Pygame serves as our dynamic visualizer to make the simulation tangible and easy to evaluate. Instead of looking at raw text outputs, the visualizer reads the parsed map coordinates and translates them into an interactive graphical interface. It handles automatic map scaling, displays real-time statistics (like the current simulation turn), and highlights different hub types using a distinct color-coding system. Most importantly, it animates the movement of drones from hub to hub, providing a clear, visual proof that our collision-avoidance and bandwidth bottleneck algorithms are working flawlessly in real time.

##**_Instructions:-**

**_Installation & Setup (Makefile)_**

This project uses `uv` as the package manager and provides a `Makefile` to automate common tasks. From the root of the repository, you can use the following commands:

* `make install`: Installs the project dependencies using `uv sync`.
* `make run`: Executes the main script.
* `make debug`: Runs the main script in debug mode using Python's built-in debugger (`pdb`).
* `make clean`: Removes temporary files and caches (e.g., `__pycache__`, `.mypy_cache`).
* `make lint`: Runs `flake8` and `mypy` to check for coding standards and type hints.
* `make build`: Builds the standalone reusable Python package (`.whl` and `.tar.gz`).

**_Running the Application_**

Use "make run" to start the program.
You can use the mouse to select a map that will show the path of drones and number of turns.
There is a mouse receptive button that allowes you to go back to select another map from here.

## **_Resources:_**

https://www.w3schools.com/python/ref_module_heapq.asp
https://docs.python.org/3/howto/regex.html
https://pypi.org/project/pygame/
https://www.pygame.org/docs/
https://fr.wikipedia.org/wiki/Algorithme_de_Dijkstra
https://www.datacamp.com/fr/tutorial/dijkstra-algorithm-in-python

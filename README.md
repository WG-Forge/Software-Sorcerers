# Software-Sorcerers
It's a pity but only one member left in our team
https://github.com/DimonDimskiy - Dmitrii Skrypnik
## How to run
For GUI implementation used PySide6, all required packages in requirements.txt. App  tested on Python 3.11.
To run the app you sould run GUI.py, login data also in GUI.py.
## Module description
**server.py** contains next classes to client-server interact:
- Server - creates socket with given parameters, sends binary requests, receives binary responces
- Connection - instantiates Server object, interacts with server through it, receives commands, and Python objects, translates it into binnary, returns Python objects

**presenter.py** 
- contains Presenter thread class with main game loop.

**model.py** contains classes to parse and store game data:
- GameMap - parse and store static game map objects
- GameState - parse and store dynamic game data
- GameActions - parse and store actions provided in previous turn / currentlly not used
- TankModel - data class that store dynamic state of each our tank

**vehicle.py** contains classes that handles bot turn logic
- VehicleFactory - factory that instantiate proper type of vehicle
- Vehicle  - superclass to all vehicle types
- VehicleType classes - inherit Vehicle, implements some diferrent logic for each type of vehicle

**cube_math.py** contains functions to handle some cubic coordinate math operations, and A* pathfinding algorithm for cubic coordinate cells

**config.py** contains constants used in app

**GUI.py** contains main window, runs Presenter as a thread

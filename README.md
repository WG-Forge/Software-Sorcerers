# Software-Sorcerers
It's a pity, but only one member left in our team
https://github.com/DimonDimskiy - Dmitrii Skrypnik
## How to run
For GUI implementation used PySide6, all required packages in requirements.txt. App  tested on Python 3.11.
To run the app you should run gui.py, login data also in gui.py.
## Module description
**server.py** contains next classes to client-server interact:
- Server - creates socket with given parameters, sends binary requests, receives binary responses
- Connection - instantiates Server object, interacts with server through it, receives commands, and Python objects, encodes it into binary, returns Python objects

**game.py** 
- contains Game thread class with main game loop.

**model.py** contains classes to parse and store game data:
- GameMap - parse and store static game map objects
- GameState - parse and store dynamic game data
- GameActions - parse and store actions provided in previous turn / currently not used
- TankModel - data class that store dynamic state of each our tank

**vehicle.py** contains classes that handles bot turn logic
- Vehicle  - superclass to all vehicle types, has a factory method to instantiate proper type of vehicle
- VehicleType classes - inherit Vehicle, implements some different logic for each type of vehicle

**cell.py** contains Cell class - extended tuple to handle some cubic coordinate math operations, and A* pathfinding algorithm.

**config folder** contains config files used in app.

**tests folder** contains some unittests.

**gui.py** contains main window, runs Game as a thread. Also contains Hex widget class, that represent map cells in main window.

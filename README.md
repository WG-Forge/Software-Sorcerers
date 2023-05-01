# Software-Sorcerers
It's a pity, but only one member left in our team
https://github.com/DimonDimskiy - Dmitrii Skrypnik

## How to run
For GUI implementation used PySide6, all required packages in requirements.txt. App  tested on Python 3.11.
To run the app you should run main.py, login data also in main.py.
Or you can run tests/test_multiplayer.py to create three bots in different threads.

## Module description
**connection.py** 
- contains Connection class that provides client-server interact

### logic folder
**game.py** 
- contains Game thread class with main game loop.

**model.py** contains classes to parse and store game data:
- GameMap - parse and store static game map objects
- GameState - parse and store dynamic game data
- GameActions - parse and store actions provided in previous turn / currently not used
- TankModel - dataclass that store dynamic state of each our tank

**vehicle.py** contains classes that handles bot turn logic
- Vehicle  - superclass to all vehicle types, has a factory method to instantiate proper type of vehicle
- VehicleType classes - inherit Vehicle, implements some different logic for each type of vehicle

**cell.py** contains Cell class - dataclass with methods that handles cubic coordinate math operations, and A* pathfinding algorithm.

### config folder
**config.py** constants used in game and client-server interact
**game_balance.py** constants that store vehicle characteristics defined by game rules

### GUI folder
**ui.py** constants used in GUI
**main_window.py** contains main window of the app 
**hex_widget.py** contains Hex QWidget class, used by main window to represent game cells in GUI

### tests folder
**test_cell.py** unittest for cell.py
**test_connection.py** unittest for connection.py
**test_multiplayer.py** alternative entry point to the app that runs three bots in different threads to test multiplayer
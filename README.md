# Software-Sorcerers
It's a pity, but only one member left in our team
https://github.com/DimonDimskiy - Dmitrii Skrypnik

## How to run
For GUI implementation used PySide6, all required packages in requirements.txt. App  tested on Python 3.11.
To run the app you should run main.py. You can run bot on multiplayer test mode by placing a checkmark in 
CheckBox next to this login option in login window. This option will block some login input fields that will
be generated automatically.

## Module description
**main.py** entry point with login data

**connection.py** contains Connection class that provides client-server interact

### logic folder
**game.py** contains Game thread class with main game loop.

**model.py** contains classes to parse and store game data:
- GameMap - parses and stores static game map objects
- GameState - parsse and stores dynamic game data
- GameActions - parses and stores actions provided in previous turn / currently not used
- TankModel - dataclass that stores dynamic state of each our tank

**vehicle.py** contains classes that handle bot turn logic:
- Vehicle  - superclass to all vehicle types, has a factory method to instantiate proper type of vehicles, implements common behavior of vehicles
- VehicleType classes - inherits Vehicle, implements different logic for each type of vehicles

**cell.py** contains Cell class - dataclass with methods that handle cubic coordinate math operations, and A* pathfinding algorithm.

### config folder
**config.py** constants used in game and client-server interactions

**game_balance.py** constants that store vehicle characteristics defined by game rules

### GUI folder
**ui.py** constants used in GUI

**main_window.py** contains main window of the app 

**hex_widget.py** contains Hex QWidget class, used by main window to represent game cells in GUI

**login_window** contains LoginWindow widget, that will be displayed in the app start to ask user for inputing login data.

### tests folder
**test_cell.py** unittest for cell.py

**test_connection.py** unittest for connection.py

# Software-Sorcerers
## Module description
**Client.py** contains next classes to client-server interact:
- Client - creates socket with given parameters, sends binary requests, receives binary responces
- Transmitter - encodes given command and Python objects into binary request
- Receiver - decode given binary response into Python objects !TODO add handling of server errors and low bufferiize error
- Dialogue - instantiates Client object, interact with server through it using Transmitter and Receiver, recieve commands, and Python objects, returns Python objects

**main.py** 
- contains Controller with main game loop

**Model.py** contains classes to parse and store game data:
- GameMap - parse and store static game map objets
- GameState - parse and store dynamic game data
- GameActions - parse and store actions provided in previous turn

**Vehicle.py** contains classes that handles bot turn logic
- VehicleFactory - factory that instantiate proper type of vehicle
- Vehicle  - superclass to all vehicle types
- VehicleType classes - inherit Vehicle, implements some diferrent logic for each type of vehicle

**cube_math.py** contains functions to handle some cubic coordinate math operations, and A* pathfinding algorithm for cubic coordinate cells



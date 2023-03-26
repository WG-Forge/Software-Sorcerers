# Software-Sorcerers
## Module description
**Client.py** contains next classes to client-server interact:
- Client - creates socket with given parameters, sends binary requests, receives binary responces
- Transmitter - encodes given command and Python objects into binary request
- Receiver - decodes given binary response into Python objects !TODO add handling of server errors and low bufferiize error
- Dialogue - instantiates Client object, interacts with server through it using Transmitter and Receiver, receives commands, and Python objects, returns Python objects

**main.py** 
- contains Controller with main game loop

**Model.py** contains classes to parse and store game data:
- GameMap - parse and store static game map objects
- GameState - parse and store dynamic game data
- GameActions - parse and store actions provided in previous turn

**Vehicle.py** contains classes that handles bot turn logic
- VehicleFactory - factory that instantiate proper type of vehicle
- Vehicle  - superclass to all vehicle types
- VehicleType classes - inherit Vehicle, implements some diferrent logic for each type of vehicle

**cube_math.py** contains functions to handle some cubic coordinate math operations, and A* pathfinding algorithm for cubic coordinate cells


<img width="690" alt="Screenshot 2023-03-26 at 23 08 36" src="https://user-images.githubusercontent.com/99563071/227804801-4d2874d4-161a-45f3-90a2-da13bea1d54d.png">

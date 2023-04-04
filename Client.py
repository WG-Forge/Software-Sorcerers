import socket
import json
from typing import Optional

import config as cf



class Client:
    def __init__(self):
        self.sock = socket.socket()

    def connect(self):
        self.sock.connect((cf.SERVER, cf.PORT))

    def disconnect(self):
        self.sock.close()

    def send(self, data: bytes):
        self.sock.send(data)

    def receive(self) -> bytes:
        response = self.sock.recv(cf.BUFFER_SIZE)
        return response


class Transmitter:
    ACTIONS = {
        "LOGIN": 1,
        "LOGOUT": 2,
        "MAP": 3,
        "GAME_STATE": 4,
        "GAME_ACTIONS": 5,
        "TURN": 6,
        "CHAT": 100,
        "MOVE": 101,
        "SHOOT": 102,
    }

    @classmethod
    def translate(cls, action: str, data: Optional[dict] = None) -> bytes:
        b_action = cls.ACTIONS[action].to_bytes(4, byteorder="little")
        if data is None:
            json_string = ""
        else:
            json_string = json.dumps(data)

        b_length = len(json_string).to_bytes(4, byteorder="little")
        message = b_action + b_length + json_string.encode("UTF-8")

        return message


class Receiver:
    status_code = {
        0: "OKEY",
        1: "BAD_COMMAND",
        2: "ACCESS_DENIED",
        3: "INAPPROPRIATE_GAME_STATE",
        4: "TIMEOUT",
        500: "INTERNAL_SERVER_ERROR"
    }

    @classmethod
    def translate(cls, answer: bytes) -> Optional[dict]:
        status = cls.status_code[int.from_bytes(answer[0:4], byteorder="little")]
        if status != "OKEY":
            raise RuntimeError(f"{status}")
        msg_length = int.from_bytes(answer[4:8], byteorder="little")
        if msg_length > cf.BUFFER_SIZE - 8:
            raise BufferError(f"Low buffer size to handle {msg_length}")
        json_part = (answer[8:]).decode("UTF-8")
        if json_part:
            return json.loads(json_part)
        return None


class Dialogue:
    def __init__(self):
        self.client = None

    def start_dialogue(self):
        if self.client is None:
            self.client = Client()
        self.client.connect()

    def end_dialogue(self):
        self.client.disconnect()

    def send(self, command: str,  data: Optional[dict] = None) -> dict:
        self.client.send(Transmitter.translate(command, data))
        return Receiver.translate(self.client.receive())


if __name__ == "__main__":
    dialogue = Dialogue()
    dialogue.start_dialogue()
    answer = dialogue.send("LOGIN", {"name": "Boris"})
    print(answer)
    answer = dialogue.send("MAP")
    print(answer)
    answer = dialogue.send("GAME_STATE")
    print(answer)
    answer = dialogue.send("LOGOUT")
    print(answer)
    dialogue.end_dialogue()

import socket
import json
from typing import Optional
import time

import config as cf


class Client:

    def __init__(self):
        self.sock = socket.socket()

    def connect(self):
        self.sock.connect((cf.SERVER, cf.PORT))

    def disconnect(self):
        self.sock.close()

    def send(self, data: bytes):
        print(data)
        self.sock.send(data)

    def receive(self) -> bytes:
        chunks = []
        init_read = self.sock.recv(8)
        status_code = int.from_bytes(init_read[0:4], byteorder="little")
        if status_code != 0:
            raise RuntimeError(f"{cf.STATUS_CODE[status_code]}")
        msg_len = int.from_bytes(init_read[4:8], byteorder="little")
        bytes_recd = 0
        while bytes_recd < msg_len:
            chunk = self.sock.recv(min(msg_len - bytes_recd, cf.BUFFER_SIZE))
            chunks.append(chunk)
            bytes_recd = bytes_recd + len(chunk)
        print(chunks)
        return b''.join(chunks)


class Dialogue:
    def __init__(self):
        self.client = None

    def start_dialogue(self):
        if self.client is None:
            self.client = Client()
        self.client.connect()

    def end_dialogue(self):
        self.client.disconnect()

    def send(self, command: str,  data: Optional[dict] = None) -> Optional[dict]:
        self.client.send(self.translate(command, data))
        response = self.client.receive()
        answer = None
        if response:
            answer = json.loads(response.decode("UTF-8"))

# <-------------logging, uncomment for debug -------
#         with open("log.txt", "a") as f:
#             f.writelines(f"{time.ctime()}, {command}, {data}\n")
#             f.write(f"{time.ctime()}, {response}\n")
# <-------------------end of logging ---------------

        return answer

    @staticmethod
    def translate(action: str, data: Optional[dict] = None) -> bytes:
        b_action = cf.ACTIONS[action].to_bytes(4, byteorder="little")
        if data is None:
            json_string = ""
        else:
            json_string = json.dumps(data)
        b_length = len(json_string).to_bytes(4, byteorder="little")
        message = b_action + b_length + json_string.encode("UTF-8")
        return message


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

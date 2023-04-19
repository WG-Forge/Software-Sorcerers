import socket
import json
from typing import Optional

from config import connection as ccf
from config.actions import Actions


class Client:

    def __init__(self):
        self.sock = socket.socket()

    def connect(self):
        self.sock.connect((ccf.SERVER, ccf.PORT))

    def disconnect(self):
        self.sock.close()

    def send(self, data: bytes):
        self.sock.send(data)

    def receive(self) -> bytes:
        chunks = []
        init_read = self.sock.recv(8)
        status_code = int.from_bytes(init_read[0:4], byteorder="little")
        msg_len = int.from_bytes(init_read[4:8], byteorder="little")
        bytes_recd = 0
        while bytes_recd < msg_len:
            chunk = self.sock.recv(min(msg_len - bytes_recd, ccf.BUFFER_SIZE))
            chunks.append(chunk)
            bytes_recd = bytes_recd + len(chunk)
        if status_code != 0:
            raise RuntimeError(f"{ccf.StatusCode(status_code)}", b''.join(chunks))
        return b''.join(chunks)


class Connection:
    def __init__(self):
        self.client = None

    def init_connection(self):
        if self.client is None:
            self.client = Client()
        self.client.connect()

    def close_connection(self):
        self.client.disconnect()

    def send(self, command: "Actions",  data: Optional[dict] = None) -> Optional[dict]:
        self.client.send(self.translate(command, data))
        response = self.client.receive()
        answer = None
        if response:
            answer = json.loads(response.decode("UTF-8"))
        return answer

    @staticmethod
    def translate(action: "Actions", data: Optional[dict] = None) -> bytes:
        b_action = action.to_bytes(4, byteorder="little")
        if data is None:
            json_string = ""
        else:
            json_string = json.dumps(data)
        b_length = len(json_string).to_bytes(4, byteorder="little")
        message = b_action + b_length + json_string.encode("UTF-8")
        return message


if __name__ == "__main__":
    connection = Connection()
    connection.init_connection()
    answer = connection.send(Actions.LOGIN, {"name": "Ivan"})
    print(answer)
    answer = connection.send(Actions.MAP)
    print(answer)
    answer = connection.send(Actions.GAME_STATE)
    print(answer)
    answer = connection.send(Actions.LOGOUT)
    print(answer)
    connection.close_connection()

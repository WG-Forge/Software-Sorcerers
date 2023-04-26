"""
This module contains classes for client-server interact
"""
import socket
import json
from typing import Optional

from config import connection as ccf
from config.actions import Actions


class Server:
    """
    Class handles socket creation
    """
    def __init__(self):
        self.sock = socket.socket()

    def connect(self):
        """
        Initiates connection to server
        :return: None
        """
        self.sock.connect((ccf.SERVER, ccf.PORT))

    def disconnect(self):
        """
        Provides disconnection from server
        :return: None
        """
        self.sock.close()

    def send(self, data: bytes):
        """
        Sends data bytes to server
        :param data: byte string
        :return: None
        """
        self.sock.send(data)

    def receive(self) -> bytes:
        """
        Reads data from socket buffer
        :return: byte string
        """
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
    """
    Creates Server obj, encode Python objects into byte strings, send it to server using Server obj,
    receive byte strings from Server obj, and decode them into Python objects
    """
    def __init__(self):
        self.client = None

    def init_connection(self):
        """
        Instantiates Server obj, initiates connection
        :return: None
        """
        if self.client is None:
            self.client = Server()
        self.client.connect()

    def close_connection(self):
        """
        Initiates disconnect from server
        :return: None
        """
        self.client.disconnect()

    def send(self, command: Actions,  data: Optional[dict] = None) -> Optional[dict]:
        """
        Took Python objects, encode them into byte strings using translate method,
        send byte strings to server using Server obj,
        receive response and decode it into Python objects, returns Python dict response
        :param command: action from enum type "Actions"
        :param data: dict | None
        :return: dict response
        """
        self.client.send(self.encode(command, data))
        response = self.client.receive()
        if response:
            return json.loads(response.decode("UTF-8"))
        return None

    @staticmethod
    def encode(action: Actions, data: Optional[dict] = None) -> bytes:
        """
        Encode action, and data into byte string
        :param action: action from enum type Actions
        :param data: Python dict | None
        :return: byte string
        """
        b_action = action.to_bytes(4, byteorder="little")
        if data is None:
            json_string = ""
        else:
            json_string = json.dumps(data)
        b_length = len(json_string).to_bytes(4, byteorder="little")
        message = b_action + b_length + json_string.encode("UTF-8")
        return message


if __name__ == "__main__":
    pass

"""
This module contains class Connection for client-server interact
"""
import socket
import json
from typing import Optional

from config import config as cf


class Connection:
    """
    Creates socket, encode Python objects into byte strings,
    send it to server using socket, receive byte strings,
    and decode them into Python objects
    """

    def __init__(self):
        self.sock = socket.socket()

    def init_connection(self):
        """
        Creates socket, with params defined in config
        :return: None
        """
        self.sock.connect((cf.SERVER, cf.PORT))

    def close_connection(self):
        """
        Initiates disconnect from server
        :return: None
        """
        self.sock.close()

    def send(self, command: cf.Actions, data: Optional[dict] = None) -> Optional[dict]:
        """
        Took Python objects, encode them into byte strings using translate method,
        send byte strings to server using Server obj,
        receive response and decode it into Python objects, returns Python dict response
        :param command: action from enum type "Actions"
        :param data: dict | None
        :return: dict response
        """
        self.sock.send(self.encode(command, data))
        response = self.receive()
        if response:
            return json.loads(response.decode("UTF-8"))
        return None

    def receive(self) -> bytes:
        """
        Reads data from socket buffer
        :return: byte string
        """
        chunks = []
        init_read = self.sock.recv(cf.RESPONSE_HEADER_SIZE)
        status_code = int.from_bytes(
            init_read[: cf.RESULT_CODE_SIZE], byteorder="little"
        )
        msg_len = int.from_bytes(
            init_read[cf.RESULT_CODE_SIZE : cf.RESPONSE_HEADER_SIZE],
            byteorder="little",
        )
        bytes_recd = 0
        while bytes_recd < msg_len:
            chunk = self.sock.recv(min(msg_len - bytes_recd, cf.BUFFER_SIZE))
            chunks.append(chunk)
            bytes_recd = bytes_recd + len(chunk)
        if status_code != cf.StatusCode.OKEY:
            raise RuntimeError(f"{cf.StatusCode(status_code)}", b"".join(chunks))
        return b"".join(chunks)

    @staticmethod
    def encode(action: cf.Actions, data: Optional[dict] = None) -> bytes:
        """
        Encode action, and data into byte string
        :param action: action from enum type Actions
        :param data: Python dict | None
        :return: byte string
        """
        b_action = action.to_bytes(cf.ACTION_ENCODE_SIZE, byteorder="little")
        if data is None:
            json_string = ""
        else:
            json_string = json.dumps(data)
        b_length = len(json_string).to_bytes(cf.LENGTH_ENCODE_SIZE, byteorder="little")
        message = b_action + b_length + json_string.encode("UTF-8")
        return message

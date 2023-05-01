import unittest

from connection import Connection
from config.config import Actions


class TestConnection(unittest.TestCase):
    def test_connection(self):
        connection = Connection()
        connection.init_connection()
        actual = connection.send(Actions.LOGIN, {"name": "Ivan"})
        self.assertIsInstance(actual, dict)
        actual = connection.send(Actions.MAP)
        self.assertIsInstance(actual, dict)
        actual = connection.send(Actions.GAME_STATE)
        self.assertIsInstance(actual, dict)
        actual = connection.send(Actions.LOGOUT)
        self.assertIsNone(actual)
        connection.close_connection()


if __name__ == "__main__":
    unittest.main()

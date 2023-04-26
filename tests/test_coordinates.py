import unittest

from coordinates import Coordinates


class TestCoordinates(unittest.TestCase):

    def test_cube_distance(self):
        cell1 = Coordinates((1, 2, -3))
        cell2 = Coordinates((1, 2, -3))
        actual = cell1.cube_distance(cell2)
        expected = 0
        self.assertEqual(expected, actual)
        cell1 = Coordinates((1, 1, -2))
        cell2 = Coordinates((0, -3, 3))
        actual = cell1.cube_distance(cell2)
        expected = 5
        self.assertEqual(expected, actual)

    def test_offset(self):
        cell1 = Coordinates((1, 1, -2))
        shift = (-1, -4, 5)
        actual = cell1.offset(shift)
        expected = (0, -3, +3)
        self.assertEqual(expected, actual)
        cell1 = Coordinates((1, -1, 0))
        shift = (-1, 1, 0)
        actual = cell1.offset(shift)
        expected = (0, 0, 0)
        self.assertEqual(expected, actual)

    def test_neighbours(self):
        cell = Coordinates((-3, 0, 3))
        actual = cell.neighbours()
        self.assertIsInstance(actual, set)
        cell = Coordinates((-3, 0, 3))
        actual = cell.neighbours()
        expected = {(-3, -1, 4), (-2, -1, 3), (-2, 0, 2),
                    (-3, 1, 2), (-4, 1, 3), (-4, 0, 4)}
        self.assertEqual(expected, actual)

    def test_in_radius(self):
        cell = Coordinates((-2, 1, 1))
        expected = cell.neighbours()
        expected.add(cell)
        actual = cell.in_radius(1)
        self.assertEqual(expected, actual)
        cell = Coordinates((1, -1, 0))
        expected = set()
        for i in cell.neighbours():
            expected.update(i.neighbours())
        actual = cell.in_radius(2)
        self.assertEqual(expected, actual)

    def test_in_radius_excl(self):
        cell = Coordinates((2, 1, -3))
        expected = cell.neighbours()
        actual = cell.in_radius_excl(0, 1)
        self.assertEqual(expected, actual)

    def test_a_star(self):
        center_cell = Coordinates((0, 0, 0))
        available_cells = center_cell.in_radius_excl(2, 3)
        start_cell = Coordinates((0, 3, -3))
        target_cell = Coordinates((-1, -2, 3))
        actual = start_cell.a_star(available_cells, target_cell)
        expected = [(-1, 3, -2), (-2, 3, -1), (-3, 3, 0), (-3, 2, 1),
                    (-3, 1, 2), (-3, 0, 3), (-2, -1, 3), (-1, -2, 3)]
        self.assertEqual(expected, actual)

    def test_normal_directions(self):
        cell = Coordinates((-1, 0, 1))
        actual = cell.normal_directions(2)
        expected = [{(0, 0, 0), (1, 0, -1)}, {(-2, 0, 2), (-3, 0, 3)},
                    {(-2, 1, 1), (-3, 2, 1)}, {(0, -1, 1), (1, -2, 1)},
                    {(-1, -1, 2), (-1, -2, 3)}, {(-1, 1, 0), (-1, 2, -1)}]
        self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()

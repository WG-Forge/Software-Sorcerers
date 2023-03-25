from itertools import permutations as perm
from collections import namedtuple
from heapq import merge


def cube_distance(hex1: tuple[int, int, int], hex2: tuple[int, int, int]) -> int:
    """
    :param hex1: coordinates (x, y, z) of first hex
    :param hex2: coordinates (x, y, z) of second hex
    :return: distance between hexes
    """
    return max(abs(i - j) for i, j in zip(hex1, hex2))


def offset(hex_: tuple[int, int, int], offset_: tuple[int, int, int]) -> tuple[int, int, int]:
    """
    :param hex_: coordinate tuple (x, y, z) of hex
    :param offset_: coordinate offset tuple (dx, dy, dz)
    :return: new coordinate tuple (x, y, z)
    """
    return tuple(i + j for i, j in zip(hex_, offset_))


def neighbours(hex_: tuple[int, int, int]) -> set[tuple[int, int, int]]:
    """
    :param hex_: coordinate tuple (x, y, z) of hex
    :return: set of neighbours coordinate tuples
    """
    return set(offset(hex_, direction) for direction in perm(range(-1, 2), 3))


def in_radius(hex_: tuple[int, int, int], radius: int) -> set[tuple[int, int, int]]:
    """
    :param hex_: coordinate tuple (x, y, z) of hex
    :param radius: radius of circle
    :return: set of hexes coordinates in given radius from given hex, includes given hex
    """
    result = set()
    for dx in range(- radius, radius + 1):
        for dy in range(max(- radius, - dx - radius), min(radius, - dx + radius) + 1):
            dz = - dx - dy
            result.add(offset(hex_, (dx, dy, dz)))
    return result


def in_radius_excl(hex_: tuple[int, int, int], small_radius: int, big_radius: int):
    """
    :param hex_: coordinate tuple (x, y, z) of hex
    :param small_radius: radius of small circle
    :param big_radius: radius of large circle
    :return: set of hexes coordinates in given large circle excluding hexes in small circle
    """
    return in_radius(hex_, big_radius).difference(in_radius(hex_, small_radius))


def a_star(map_cells: set[tuple[int, int, int]], start: tuple[int, int, int],
           finish: tuple[int, int, int]) -> list[tuple[int, int, int]]:
    """
    A* pathfinding algorithm
    :param map_cells: set of available map cells excluding spawn points, obstacles
    :param start: starting cell
    :param finish: target cell
    :return: list with path coordinate tuples excluding start point
    """
    Node = namedtuple("node", ['coords', 'previous'])
    start = Node(start, None)

    def build_path(to_node):
        path = []
        while not(to_node.previous is None):
            path.append(to_node.coords)
            to_node = to_node.previous
        return path[::-1]

    reachable = [start, ]
    explored = set()
    while reachable:
        current_node = reachable.pop(0)
        if current_node.coords == finish:
            return build_path(current_node)
        explored.add(current_node.coords)
        new_reachable = [i for i in (neighbours(current_node.coords).difference(explored)).intersection(map_cells)]
        tmp = []
        for node in new_reachable:
            if node not in (i.coords for i in reachable):
                node = Node(node, current_node)
                tmp.append(node)
        tmp.sort(key=lambda x: cube_distance(x.coords, finish))
        reachable = list(merge(reachable, tmp, key=lambda x: cube_distance(x.coords, finish)))





if __name__ == "__main__":
    assert cube_distance((1, 2, -3), (1, 2, -3)) == 0
    assert cube_distance((1, 1, -2), (0, -3, 3)) == 5
    assert offset((1, 1, -2), (-1, -4, 5)) == (0, -3, +3)
    assert offset((1, -1, 0), (-1, 1, 0)) == (0, 0, 0)
    assert neighbours((-3, 0, 3)) == {(-3, -1, 4), (-2, -1, 3), (-2, 0, 2), (-3, 1, 2), (-4, 1, 3), (-4, 0, 4)}
    assert neighbours((1, 1, -2)) == in_radius_excl((1, 1, -2), 0, 1)
    expected = set()
    for i in neighbours((1, -1, 0)):
        expected.update(neighbours(i))
    assert expected == in_radius((1, -1, 0), 2)

map_cells = in_radius((0, 0, 0),4)
start = (0, 3, -3)
finish = (-2, -1, 3)
print(a_star(map_cells, start, finish))

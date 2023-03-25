from itertools import permutations as perm


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

from itertools import permutations as perm


def cube_distance(hex1: tuple[int], hex2: tuple[int]) -> int:
    """
    :param hex1: coordinates (x, y, z) of first hex
    :param hex2: coordinates (x, y, z) of second hex
    :return: distance between hexes
    """
    return max(abs(i - j) for i, j in zip(hex1, hex2))


def offset(hex_: tuple[int], offset_: tuple[int]) -> tuple[int]:
    """
    :param hex_: coordinate tuple (x, y, z) of hex
    :param offset_: coordinate offset tuple (dx, dy, dz)
    :return: new coordinate tuple (x, y, z)
    """
    return tuple(i + j for i, j in zip(hex_, offset_))


def neighbours(hex_: tuple[int]) -> set[tuple[int]]:
    """
    :param hex_: coordinate tuple (x, y, z) of hex
    :return: set of neighbours coordinate tuples
    """
    return set(offset(hex_, direction) for direction in perm(range(-1, 2), 3))


def in_radius(hex_: tuple[int], radius: int) -> set[tuple[int]]:
    for dx in range(- radius, radius + 1):
        ...


def cube_add():
    pass


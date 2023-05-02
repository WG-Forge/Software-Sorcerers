"""
This module contains Cell dataclass,
it provides methods to work with coordinate cells
"""
import dataclasses
from collections import namedtuple
from itertools import permutations


@dataclasses.dataclass(frozen=True, eq=True, match_args=True)
class Cell:
    """
    Dataclass that represents coordinate cell, provide
    methods to work with cubic coordinates
    """

    x: int
    y: int
    z: int

    def __iter__(self):
        return iter(dataclasses.astuple(self))

    def cube_distance(self, other) -> int:
        """
        :param other: Cell obj
        :return: distance between hexes
        """
        return max(abs(i - j) for i, j in zip(self, other))

    def offset(self, offset_: tuple[int, int, int]) -> "Cell":
        """
        :param offset_: coordinate offset tuple (dx, dy, dz)
        :return: Cell obj
        """
        return Cell(*(i + j for i, j in zip(self, offset_)))

    def neighbours(self) -> set["Cell"]:
        """
        :return: set of neighbours coordinate tuples
        """
        return set(
            self.offset(direction) for direction in permutations(range(-1, 2), 3)
        )

    def in_radius(self, radius: int) -> set["Cell"]:
        """
        :param radius: radius of circle
        :return: set of Cell obj in given radius from self, includes self
        """
        result = set()
        for d_x in range(-radius, radius + 1):
            for d_y in range(
                max(-radius, -d_x - radius), min(radius, -d_x + radius) + 1
            ):
                d_z = -d_x - d_y
                result.add(self.offset((d_x, d_y, d_z)))
        return result

    def normal_directions(self, radius: int) -> list[set["Cell"]]:
        """
        :param radius: maximum cells on each direction
        :return: list of sets of Cell for each normal direction for self, in given radius
        """
        x_positive_dir = {
            self.offset((delta, 0, -delta)) for delta in range(1, radius + 1)
        }
        x_negative_dir = {
            self.offset((-delta, 0, delta)) for delta in range(1, radius + 1)
        }
        y_positive_dir = {
            self.offset((-delta, delta, 0)) for delta in range(1, radius + 1)
        }
        y_negative_dir = {
            self.offset((delta, -delta, 0)) for delta in range(1, radius + 1)
        }
        z_positive_dir = {
            self.offset((0, -delta, delta)) for delta in range(1, radius + 1)
        }
        z_negative_dir = {
            self.offset((0, delta, -delta)) for delta in range(1, radius + 1)
        }
        return [
            x_positive_dir,
            x_negative_dir,
            y_positive_dir,
            y_negative_dir,
            z_positive_dir,
            z_negative_dir,
        ]

    def in_radius_excl(self, small_radius: int, big_radius: int) -> set["Cell"]:
        """
        :param small_radius: radius of small circle
        :param big_radius: radius of large circle
        :return: set of Cell in given large circle excluding hexes in small circle
        """
        return self.in_radius(big_radius).difference(self.in_radius(small_radius))

    def a_star(self, map_cells: set["Cell"], finish: "Cell") -> list["Cell"]:
        """
        A* pathfinding algorithm
        :param map_cells: set of available map cells excluding spawn points, obstacles
        :param finish: target cell
        :return: list with path Cell excluding self coordinates
        """
        Node = namedtuple("Node", ["cell", "previous"])
        start = Node(self, None)

        def build_path(to_node: Node) -> list["Cell"]:
            path = []
            while to_node.previous:
                path.append(to_node.cell)
                to_node = to_node.previous
            return path[::-1]

        reachable = [
            start,
        ]
        explored = set()
        while reachable:
            current_node = min(reachable, key=lambda x: x[0].cube_distance(finish))
            reachable.remove(current_node)
            if current_node.cell == finish:
                return build_path(current_node)
            explored.add(current_node.cell)
            new_nodes = list(
                current_node.cell.neighbours()
                .difference(explored)
                .intersection(map_cells)
            )
            for node in new_nodes:
                if node not in (i.cell for i in reachable):
                    node = Node(node, current_node)
                    reachable.append(node)

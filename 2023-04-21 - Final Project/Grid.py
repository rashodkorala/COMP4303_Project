from typing import List, Tuple
class Grid:
    def __init__(self, x: int, z: int):
        self.x = x
        self.z = z
        self._grid = [[0] * z for _ in range(x)]

    def set_grid(self, x: int, z: int, type: int):
        self._grid[x][z] = type

    def get_grid(self, x: int, z: int) -> int:
        return self._grid[x][z]

    def width(self) -> int:
        return self.x

    def height(self) -> int:
        return self.z

    def is_oob(self, x: int, z: int) -> bool:
        return x < 0 or z < 0 or x >= self.width() or z >= self.height()

    def is_type(self, x: int, z: int, type: int) -> bool:
        return self._grid[x][z] == type

    def get_goals(self) -> List[Tuple[int, int]]:
        goals = []
        for x in range(self.width()):
            for z in range(self.height()):
                if self.is_type(x, z, 3):
                    goals.append((x, z))
        return goals


class Node:
    def __init__(self, x: int, z: int, parent: 'Node' = None):
        self.x = x
        self.z = z
        self.parent = parent

    def __eq__(self, other: 'Node') -> bool:
        return self.x == other.x and self.z == other.z

    def __str__(self) -> str:
        return f'({self.x}, {self.z})'

    def __repr__(self) -> str:
        return self.__str__()
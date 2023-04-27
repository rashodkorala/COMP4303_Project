from typing import List, Tuple

# 0 for empty space
# 1 for obstacles , and walls

#2 for Roads 

#3 for goals

#buildings can be only placeed on 0 and area building takes on the grid is marked as 1
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



# from ast import List, Tuple
# import noise
# import numpy as np


# class Grid:
#     def __init__(self, x: int, z: int, scale: float = 0.1, threshold: float = 0.6):
#         self.x = x
#         self.z = z
#         self.scale = scale
#         self.threshold = threshold
#         self._grid = [[0] * z for _ in range(x)]
#         self.generate_perlin_noise()

#     def generate_perlin_noise(self):
#         for x in range(self.x):
#             for z in range(self.z):
#                 noise_val = (noise.pnoise2(x * self.scale, z * self.scale) + 1) / 2
#                 if noise_val > self.threshold:
#                     self.set_grid(x, z, 1)  # Mark the cell as occupied by a structure
#                 else:
#                     self.set_grid(x, z, 0)  # Mark the cell as empty

#     def set_grid(self, x: int, z: int, type: int):
#         self._grid[x][z] = type

#     def get_grid(self, x: int, z: int) -> int:
#         return self._grid[x][z]

#     def width(self) -> int:
#         return self.x

#     def height(self) -> int:
#         return self.z

#     def is_oob(self, x: int, z: int) -> bool:
#         return x < 0 or z < 0 or x >= self.width() or z >= self.height()

#     def is_type(self, x: int, z: int, type: int) -> bool:
#         return self._grid[x][z] == type

#     def get_goals(self) -> List[Tuple[int, int]]:
#         goals = []
#         for x in range(self.width()):
#             for z in range(self.height()):
#                 if self.is_type(x, z, 3):
#                     goals.append((x, z))
#         return goals

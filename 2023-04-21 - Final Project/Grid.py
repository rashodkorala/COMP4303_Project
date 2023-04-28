import heapq
from typing import List, Tuple

import numpy as np

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
    def print_grid(self):
        for row in self._grid:
            for cell in row:
                print(cell, end=' ')
            print()


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

def heuristic(a: Tuple[int, int], b: Tuple[int, int]) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def a_star_search(grid: Grid, start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
    frontier = []
    heapq.heappush(frontier, (0, start))
    came_from = {start: None}
    cost_so_far = {start: 0}

    while frontier:
        _, current = heapq.heappop(frontier)

        if current == goal:
            break

        for dx, dz in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            next_cell = (current[0] + dx, current[1] + dz)

            if grid.is_oob(next_cell[0], next_cell[1]) or grid.is_type(next_cell[0], next_cell[1], 1):
                continue

            new_cost = cost_so_far[current] + 1
            if next_cell not in cost_so_far or new_cost < cost_so_far[next_cell]:
                cost_so_far[next_cell] = new_cost
                priority = new_cost + heuristic(goal, next_cell)
                heapq.heappush(frontier, (priority, next_cell))
                came_from[next_cell] = current

    # Reconstruct the path
    if goal in came_from:
        path = [goal]
        while path[-1] != start:
            path.append(came_from[path[-1]])
        path.reverse()
        return path
    else:
        return None  # No path found
    

def build_paths_from_grid(editor, grid,blockType, begin,heigtmap):
    road_block = "minecraft:soul_sand"
    # begin=[buildRect[0],0,buildRect[1]]
    print("building paths")
    for x in range(grid.width()):
        for z in range(grid.height()):
            if grid.get_grid(x, z) == 2:
                print("building road at", x, z)
                y = heigtmap[(x,z)] 
                print("y",y)
                pos = begin + np.array([x, y, z])
                editor.placeBlock(pos, blockType)

def setRods(grid):
    #set start and end points
    goals=grid.get_goals()
    start=goals[0]
    print("start",start)
    previus_goal=start
    #find path from start to end
    for goal in goals:
        path = a_star_search(grid, start, goal)
        if path is not None:
            for x, z in path:
                grid.set_grid(x, z, 2)
            previus_goal=goal
    else:
        print("No path found")
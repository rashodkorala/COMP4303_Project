import sys
sys.path.append("setup_files")


from buildArea_calc import *



editor, world_slice, build_rect, build_area, heightmap = set_build_area()

#Setting up editor
#Setting up build area and heightmap
#Flattening the build area
#editor, world_slice, build_rect, build_area, heightmap = set_cleared_area()



""" # Placing walls
print("Placing walls...")
for point in build_rect.outline:
    height = heightmap[tuple(point - build_rect.offset)]
    #building a wall

    for y in range(height, height+9):
        # Place the first layer of blocks
        editor.placeBlock(addY(point, y), Block("cobblestone"))  """
     
 


#Create village
sys.path[0] = sys.path[0].removesuffix('\\biomes\\snow')
from structures_setup import *
from road_system import *


def buildRoadAroundbuildings(editor, WORLDSLICE, grid, BuildingBeginX, BuildingBeginZ, width, depth):
    print("Started building road around town hall")

    start_x = BuildingBeginX - 1  # -1 to make sure the road is not built on the building
    start_z = BuildingBeginZ - 1  # -1 to make sure the road is not built on the building
    end_x = start_x + width + 3  # +2 to make sure the road is not built on the building
    end_z = start_z + depth + 3  # +2 to make sure the road is not built on the building
    y = -1

    road_block = "minecraft:dirt_path"  # Replace with the desired road block type
    #set the middle block of the road to goal
    
    # Build the top and bottom horizontal roads
    for x in range(start_x, end_x):
        pos=build_area.begin+[x,y,start_z]
        pos2=build_area.begin+[x,y,end_z-1]
        # editor.placeBlock(pos, Block(road_block))
        # editor.placeBlock(pos2, Block(road_block))
        if  (grid.is_oob(x, start_z)==False):
            grid.set_grid(x,start_z,2)
            grid.set_grid(x,end_z-1,2)
        

    # Build the left and right vertical roads
    for z in range(start_z+1, end_z-1):
        pos=build_area.begin+[start_x,y,z]
        pos2=build_area.begin+[end_x-1,y,z]
        # editor.placeBlock(pos, Block(road_block))
        # editor.placeBlock(pos2, Block(road_block))
        if  (grid.is_oob(start_x, z)==False):
            grid.set_grid(start_x,z,2)
            grid.set_grid(end_x-1,z,2)

    grid.set_grid(start_x,start_z,3)
    editor.placeBlock((build_area.begin.x+start_x,build_area.begin.y,build_area.begin.z+start_z), Block("minecraft:gold_block"))
    print("Finished building road around town hall")


from collections import deque

from collections import deque
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

""" def bfs_search(grid: Grid, start: Tuple[int, int]) -> List[Tuple[int, int]]:
    visited = set()
    queue = deque([(start, 0, None)])  # Add parent to the queue element
    parents = {}  # Keep track of parents for each visited cell
    goals_distances = []

    while queue:
        (x, z), distance, parent = queue.popleft()
        if grid.is_oob(x, z) or (x, z) in visited:
            continue

        visited.add((x, z))
        parents[(x, z)] = parent

        if grid.is_type(x, z, 1):  # Obstacle
            continue

        if grid.is_type(x, z, 3):  # Goal
            goals_distances.append(((x, z), distance))

            # Reconstruct the path from start to goal
            path = [(x, z)]
            while parents[path[-1]] is not None:
                path.append(parents[path[-1]])

            # Set the path in the grid as roads
            for px, pz in path[:-1]:  # Exclude the start position
                grid.set_grid(px, pz, 2)

        for dx, dz in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, nz = x + dx, z + dz
            if (nx, nz) not in visited:
                queue.append(((nx, nz), distance + 1, (x, z)))  # Add current cell as parent

    return goals_distances """

def build_paths_from_grid(editor, grid):
    road_block = "minecraft:dirt_path"
    y = -1
    print("building paths")
    for x in range(grid.width()):
        for z in range(grid.height()):
            if grid.get_grid(x, z) == 2:
                print("building road at", x, z)
                pos = build_area.begin + [x, y, z]
                editor.placeBlock(pos, Block(road_block))

    # Build the left and right vertical roads
    for z in range(start_z+1, end_z-1):
        pos=build_area.begin+[start_x,y,z]
        pos2=build_area.begin+[end_x-1,y,z]
        # editor.placeBlock(pos, Block(road_block))
        # editor.placeBlock(pos2, Block(road_block))
        grid.set_grid(start_x,z,2)
        grid.set_grid(end_x-1,z,2)

    grid.set_grid(start_x,start_z,3)
    editor.placeBlock((build_area.begin.x+start_x,build_area.begin.y,build_area.begin.z+start_z), Block("minecraft:gold_block"))
    print("Finished building road around town hall")


from collections import deque

from collections import deque
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

""" def bfs_search(grid: Grid, start: Tuple[int, int]) -> List[Tuple[int, int]]:
    visited = set()
    queue = deque([(start, 0, None)])  # Add parent to the queue element
    parents = {}  # Keep track of parents for each visited cell
    goals_distances = []

    while queue:
        (x, z), distance, parent = queue.popleft()
        if grid.is_oob(x, z) or (x, z) in visited:
            continue

        visited.add((x, z))
        parents[(x, z)] = parent

        if grid.is_type(x, z, 1):  # Obstacle
            continue

        if grid.is_type(x, z, 3):  # Goal
            goals_distances.append(((x, z), distance))

            # Reconstruct the path from start to goal
            path = [(x, z)]
            while parents[path[-1]] is not None:
                path.append(parents[path[-1]])

            # Set the path in the grid as roads
            for px, pz in path[:-1]:  # Exclude the start position
                grid.set_grid(px, pz, 2)

        for dx, dz in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, nz = x + dx, z + dz
            if (nx, nz) not in visited:
                queue.append(((nx, nz), distance + 1, (x, z)))  # Add current cell as parent

    return goals_distances """

def build_paths_from_grid(editor, grid):
    road_block = "minecraft:dirt_path"
    y = -1
    print("building paths")
    for x in range(grid.width()):
        for z in range(grid.height()):
            if grid.get_grid(x, z) == 2:
                print("building road at", x, z)
                pos = build_area.begin + [x, y, z]
                editor.placeBlock(pos, Block(road_block))

folder_path = 'biomes\snow\snow_structures' # replace with the actual folder path
file_paths = get_files(folder_path)
build_area_size = build_area.size
draw_buildings = True

# draw_roads = draw_roads(file_paths, build_area_size, build_area, editor)
grid=Grid(build_area_size.x, build_area_size.z)
placed_buildings= place_or_get_buildings(draw_buildings, file_paths, build_area_size, build_area, editor,  100, grid,bunker_height=-4 )
print(placed_buildings)
# buildRoadAroundbuildings(editor, world_slice, grid,placed_buildings.,placed_buildings[0][1],placed_buildings[0][2],placed_buildings[0][3])
for item in placed_buildings:
    building_x = item['x']
    building_z = item['z']
    width = item['width']
    depth = item['depth']
    buildRoadAroundbuildings(editor, world_slice, grid, building_x, building_z,width,depth)

#pathfinding using A* algorithm
import heapq
from typing import List, Tuple

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


build_paths_from_grid(editor, grid)

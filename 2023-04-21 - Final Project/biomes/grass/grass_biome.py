import sys
sys.path.append("setup_files")

from buildArea_calc import *


editor, world_slice, build_rect, build_area, heightmap = set_build_area()

#Setting up editor
#Setting up build area and heightmap
#Flattening the build area
#editor, world_slice, build_rect, build_area, heightmap = set_cleared_area()




# Placing walls
print("Placing walls...")
for point in build_rect.outline:
    height = heightmap[tuple(point - build_rect.offset)]
    #building a wall
    for y in range(height, height+9):
        # Place the first layer of blocks
        editor.placeBlock(addY(point, y), Block("cobblestone")) 
      

#Create village
sys.path[0] = sys.path[0].removesuffix('\\biomes\\grass')
from structures_setup import *
from road_system import *

#create a grid from the build area

GRID_TYPES = {
    "NONE": 0,
    "OBSTACLE": 1,
    "ROAD": 2,
    "GOAL": 3,
}

ACTIONS = [[-1,0],[0,-1],[1,0],[0,1]]
DIRECTIONS = ["north", "east", "south", "west"]

class Node:
        def __init__(self,x,y,action,parent):
            self.x = x
            self.y = y
            self.parent = parent
            self.g = 0
            self.h = 0
            self.f = 0
            self.action = action
class Grid:
    def __init__(self, x, z):
        self._grid = [[GRID_TYPES["NONE"]] * z for i in range(x)]
        self.x = x
        self.z = z
    
    def set_grid(self, x, z, type):
        if type == GRID_TYPES["GOAL"]:
            print("Goal located at:", x, z)
        self._grid[x][z] = type
    
    def get_grid(self, x, z):
        return self._grid[x][z]
        
    def width(self):
        return self.x

    def height(self):
        return self.z

    def is_oob(self, x, z):
        return x < 30 or z < 30 or x >= self.width() or z >= self.height()
    
    def is_type(self, x, z, type):
        return self._grid[x][z] == type

# def buildRoadAroundbuildings(editor, WORLDSLICE, grid,building_x,building_z,width,depth):
#     print("Started building road around town hall")
#     start_x = building_x+build_area.begin.x-1
#     start_z = building_z+build_area.begin.z-1
#     end_x = start_x + width+2
#     end_z = start_z + depth+2
#     for i in range(start_x, end_x):
#         for j in range(2):
#             block = editor.getBlock((i,WORLDSLICE.heightmaps["MOTION_BLOCKING_NO_LEAVES"][(i,start_z+j)]-1,start_z+j))
#             road = "oak_planks" if block == "minecraft:water" else "dirt_path"
#             editor.placeBlock((i,WORLDSLICE.heightmaps["MOTION_BLOCKING"][(i,start_z+j)]-1,start_z+j), Block(road))
#             block = editor.getBlock((i,WORLDSLICE.heightmaps["MOTION_BLOCKING_NO_LEAVES"][(i,end_z-j)]-1,end_z-j))
#             road = "oak_planks" if block == "minecraft:water" else "dirt_path"
#             editor.placeBlock((i,WORLDSLICE.heightmaps["MOTION_BLOCKING"][(i,end_z-j)]-1,end_z-j), Block(road))
#             grid.set_grid(i,start_z+j,GRID_TYPES["ROAD"])
#             grid.set_grid(i,end_z-j,GRID_TYPES["ROAD"])
    
#     for i in range(start_z, end_z):
#         for j in range(2):
#             block = editor.getBlock((start_x+j,WORLDSLICE.heightmaps["MOTION_BLOCKING_NO_LEAVES"][(start_x+j,i)]-1,i))
#             road = "oak_planks" if block == "minecraft:water" else "dirt_path"
#             editor.placeBlock((start_x+j,WORLDSLICE.heightmaps["MOTION_BLOCKING"][(start_x+j,i)]-1,i), Block(road))
#             block = editor.getBlock((end_x-j,WORLDSLICE.heightmaps["MOTION_BLOCKING_NO_LEAVES"][(end_x-j,i)]-1,i))
#             road = "oak_planks" if block == "minecraft:water" else "dirt_path"
#             editor.placeBlock((end_x-j,WORLDSLICE.heightmaps["MOTION_BLOCKING"][(end_x-j,i)]-1,i), Block(road))
#             grid.set_grid(start_x+j,i,GRID_TYPES["ROAD"])
#             grid.set_grid(end_x-j,i,GRID_TYPES["ROAD"])
#     print("Finished building road around town hall")

def buildRoadAroundbuildings(editor, WORLDSLICE, grid, BuildingBeginX, BuildingBeginZ, width, depth):
    print("Started building road around town hall")

    start_x = BuildingBeginX - 2  # -1 to make sure the road is not built on the building
    start_z = BuildingBeginZ - 2  # -1 to make sure the road is not built on the building
    end_x = start_x + width + 3  # +2 to make sure the road is not built on the building
    end_z = start_z + depth + 3  # +2 to make sure the road is not built on the building
    y = -1

    road_block = "minecraft:dirt_path"  # Replace with the desired road block type
    #set the middle block of the road to goal
    grid.set_grid(start_x,start_z,GRID_TYPES["GOAL"])
    editor.placeBlock((build_area.begin.x+start_x,0,build_area.begin.z+start_z), Block("minecraft:gold_block"))
    # Build the top and bottom horizontal roads
    for x in range(start_x, end_x):
        pos=build_area.begin+[x,y,start_z]
        pos2=build_area.begin+[x,y,end_z-1]
        # editor.placeBlock(pos, Block(road_block))
        # editor.placeBlock(pos2, Block(road_block))
        grid.set_grid(x,start_z,GRID_TYPES["ROAD"])
        grid.set_grid(x,end_z-1,GRID_TYPES["ROAD"])
        

    # Build the left and right vertical roads
    for z in range(start_z+1, end_z-1):
        pos=build_area.begin+[start_x,y,z]
        pos2=build_area.begin+[end_x-1,y,z]
        # editor.placeBlock(pos, Block(road_block))
        # editor.placeBlock(pos2, Block(road_block))
        grid.set_grid(start_x,z,GRID_TYPES["ROAD"])
        grid.set_grid(end_x-1,z,GRID_TYPES["ROAD"])

    print("Finished building road around town hall")


from collections import deque

# def bfs_search(grid, start_node, end_node):
#     queue = deque([start_node])
#     visited = set([(start_node.x, start_node.y)])

#     while queue:
#         current_node = queue.popleft()

#         if current_node.x == end_node.x and current_node.y == end_node.y:
#             path = []
#             while current_node.parent:
#                 path.append(current_node.action)
#                 current_node = current_node.parent
#             return path[::-1]

#         for action, direction in enumerate(ACTIONS):
#             new_x, new_y = current_node.x + direction[0], current_node.y + direction[1]

#             if (new_x, new_y) in visited or grid.is_oob(new_x, new_y) or grid.is_type(new_x, new_y, GRID_TYPES["OBSTACLE"]):
#                 continue

#             new_node = Node(new_x, new_y, DIRECTIONS[action], current_node)
#             queue.append(new_node)
#             visited.add((new_x, new_y))

#     return None

from collections import deque

def bfs(grid, start_pos, goal):
    def reconstruct_path(came_from, current_node):
        path = []
        while current_node is not None:
            path.append((current_node.x, current_node.y))
            current_node = came_from[current_node]
        return path[::-1]

    start_node = Node(start_pos[0], start_pos[1], None, None)
    goal_node = Node(goal[0], goal[1], None, None)

    visited = [[False for _ in range(grid.height())] for _ in range(grid.width())]
    visited[start_node.x][start_node.y] = True

    came_from = dict()
    queue = deque([start_node])

    while queue:
        current_node = queue.popleft()

        if current_node.x == goal_node.x and current_node.y == goal_node.y:
            print("Found path")
            return reconstruct_path(came_from, current_node)

        for action in ACTIONS:
            next_x, next_y = current_node.x + action[0], current_node.y + action[1]

            if (grid.is_oob(next_x, next_y) or 
                visited[next_x][next_y] or 
                grid.is_type(next_x, next_y, GRID_TYPES["OBSTACLE"])):
                continue

            next_node = Node(next_x, next_y, action, current_node)
            visited[next_x][next_y] = True
            came_from[next_node] = current_node
            queue.append(next_node)

    print("Failed to find path")
    return None  # No path found


def connect_goals_bfs(grid):
    goal_nodes = find_goals(grid)
    paths = []

    for i in range(len(goal_nodes) - 1):
        start_node = goal_nodes[i]
        end_node = goal_nodes[i + 1]
        path = bfs(grid, start_node, end_node)

        if path is not None:
            paths.append(path)
        else:
            print(f"Failed to connect goals {i} and {i + 1}")

    return paths



import heapq

def heuristic(node1, node2):
    return abs(node1.x - node2.x) + abs(node1.y - node2.y)

def a_star_search(grid, start_node, end_node):
    print("Started A* search")
    open_list = []
    closed_list = set()

    heapq.heappush(open_list, (start_node.f, start_node))

    while open_list:
        _, current_node = heapq.heappop(open_list)
        closed_list.add((current_node.x, current_node.y))

        if current_node.x == end_node.x and current_node.y == end_node.y:
            path = []
            while current_node.parent:
                path.append(current_node.action)
                current_node = current_node.parent
            return path[::-1]

        for action, direction in enumerate(ACTIONS):
            new_x, new_y = current_node.x + direction[0], current_node.y + direction[1]

            if grid.is_oob(new_x, new_y) or grid.is_type(new_x, new_y, GRID_TYPES["OBSTACLE"]):
                continue

            new_node = Node(new_x, new_y, DIRECTIONS[action], current_node)
            if (new_node.x, new_node.y) in closed_list:
                continue

            new_node.g = current_node.g + 1
            new_node.h = heuristic(new_node, end_node)
            new_node.f = new_node.g + new_node.h

            for _, existing_node in open_list:
                if existing_node.x == new_node.x and existing_node.y == new_node.y and existing_node.g < new_node.g:
                    break
            else:
                heapq.heappush(open_list, (new_node.f, new_node))

    return None

def find_goals(grid):
    print("finding goals")
    goal_nodes = []
    for x in range(grid.width()):
        for z in range(grid.height()):
            if grid.is_type(x, z, GRID_TYPES["GOAL"]):
                goal_nodes.append(Node(x, z, None, None))
    return goal_nodes

def connect_goals(grid):
    print("connecting goals")
    goal_nodes = find_goals(grid)
    paths = []

    for i in range(len(goal_nodes) - 1):
        start_node = goal_nodes[i]
        end_node = goal_nodes[i + 1]
        path = a_star_search(grid, start_node, end_node)

        if path is not None:
            paths.append(path)
        else:
            print(f"Failed to connect goals {i} and {i + 1}")

    return paths

def place_blocks(grid, paths):
    for path in paths:
        current_node = path[0]
        for action in path:
            dx, dy = action
            x, y = current_node.x + dx, current_node.y + dy

            if not grid.is_type(x, y, GRID_TYPES["GOAL"]):
                grid.set_grid(x, y, GRID_TYPES["ROAD"])
            current_node = Node(x, y, action, current_node)

def build_paths_from_grid(editor, grid):
    road_block = "minecraft:dirt_path"
    y = -1
    print("building paths")
    for x in range(grid.width()):
        for z in range(grid.height()):
            if grid.get_grid(x, z) == GRID_TYPES["ROAD"]:
                print("building road at", x, z)
                pos = build_area.begin + [x, y, z]
                editor.placeBlock(pos, Block(road_block))



folder_path = 'biomes\grass\grass_structures' # replace with the actual folder path
file_paths = get_files(folder_path)
build_area_size = build_area.size
draw_buildings = True

# draw_roads = draw_roads(file_paths, build_area_size, build_area, editor)
grid=Grid(build_area_size.x+1, build_area_size.z+1)
placed_buildings,grid = place_or_get_buildings(draw_buildings, file_paths, build_area_size, build_area, editor,  100, grid,GRID_TYPES=GRID_TYPES)
print(placed_buildings)
# buildRoadAroundbuildings(editor, world_slice, grid,placed_buildings.,placed_buildings[0][1],placed_buildings[0][2],placed_buildings[0][3])
for item in placed_buildings:
    building_x = item['x']
    building_z = item['z']
    width = item['width']
    depth = item['depth']
    buildRoadAroundbuildings(editor, world_slice, grid, building_x, building_z,width,depth)

# paths=connect_goals(grid)
# place_blocks(grid, paths)
# build_paths_from_grid(editor, grid)

paths = connect_goals_bfs(grid)
place_blocks(grid, paths)
build_paths_from_grid(editor, grid)



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


def buildRemainingRoads(STARTX, STARTZ, ENDX, ENDZ, grid, editor, WORLDSLICE):
    print("Started building remaining roads")
    # find "GOALS" in the grid
    center_x = (STARTX + ENDX) // 2
    center_z = (STARTZ + ENDZ) // 2
    for i in range(STARTX, grid.width()):
        for j in range(STARTZ,grid.height()):
            if grid.get_grid(i,j) == GRID_TYPES["GOAL"]:
                # Initialize a open list (x,y,)
                open_list = []
                # Initialize a closed list
                closed_list = [[0] * grid.height() for i in  range(grid.width())]
                node = Node(i,j,None,None)
                open_list.append(node)

                while len(open_list) > 0:
                    # Find the node with the lowest f value
                    lowest_f = open_list[0].f
                    lowest_f_index = 0
                    for k in range(len(open_list)):
                        if open_list[k].f < lowest_f:
                            lowest_f = open_list[k].f
                            lowest_f_index = k
                    current_node = open_list[lowest_f_index]
                    # Remove the node from the open list
                    open_list.pop(lowest_f_index)
                    # Add the node to the closed list
                    closed_list[current_node.x][current_node.y] = 1
                    # # Check if the node is a road
                    if grid.get_grid(current_node.x,current_node.y) == GRID_TYPES["ROAD"]:
                        # If it is, build the road
                        path = []
                        while current_node.parent != None:
                            path.append(current_node.action)
                            current_node = current_node.parent
                        path.reverse()
                        grid.set_grid(i,j,GRID_TYPES["ROAD"])
                        grid.set_grid(i,j,GRID_TYPES["ROAD"])
                        editor.placeBlock(i,WORLDSLICE.heightmaps["MOTION_BLOCKING"][(i,j)]-1,j, "grass_path")
                        buildRoadForAstar(path,i,j)
                        break
                    # Find the neighbors of the current node
                    for action in ACTIONS:
                        neighbor_x = current_node.x + action[0]
                        neighbor_y = current_node.y + action[1]
                        if grid.is_oob(neighbor_x, neighbor_y) or grid.is_type(neighbor_x, neighbor_y, GRID_TYPES["OBSTACLE"]) or closed_list[neighbor_x][neighbor_y] == 1 or grid.is_type(neighbor_x, neighbor_y, GRID_TYPES["GOAL"]):
                            continue
                        node = Node(neighbor_x,neighbor_y,action,current_node)
                        node.g = current_node.g + 1
                        node.h = abs(neighbor_x - center_x) + abs(neighbor_y - center_z)
                        node.f = node.g + node.h
                        open_list.append(node)
                        closed_list[neighbor_x][neighbor_y] = 1
                    

                    

    print("Finished building remaining roads")


    center_x = (STARTX + ENDX) // 2
    center_z = (STARTZ + ENDZ) // 2
    for i in range(STARTX, grid.width()):
        for j in range(STARTZ,grid.height()):
            if grid.is_type(i,j,GRID_TYPES["GOAL"]):
                print("Found goal at", i, j)
                dx = i - center_x
                dz = j - center_z
                print("Ec distance:", dx, dz)
                for x in range(i,abs(dx)):
                    if dx > 0:
                        editor.placeBlock(i+x,WORLDSLICE.heightmaps["MOTION_BLOCKING"][(x+i,j)]-1,j, "grass_path")
                        print("Building road at", i+x, j)
                        if grid.is_type(x+i,j,GRID_TYPES["ROAD"]):
                            break
                        grid.set_grid(i+x,j,GRID_TYPES["ROAD"])
                        
                    else:
                        editor.placeBlock(i-x,WORLDSLICE.heightmaps["MOTION_BLOCKING"][(i-x,j)]-1,j, "grass_path")
                        print("Building road at", i-x, j)
                        if grid.is_type(i-x,j,GRID_TYPES["ROAD"]):
                            break
                        grid.set_grid(i-x,j,GRID_TYPES["ROAD"])
                for z in range(j,abs(dz)):
                    if dz > 0:
                        editor.placeBlock(i,WORLDSLICE.heightmaps["MOTION_BLOCKING"][(i,j+z)]-1,j+z, "grass_path")
                        print("Building road at", i, j+z)
                        if grid.is_type(i,j+z,GRID_TYPES["ROAD"]):
                            break
                        grid.set_grid(i,j+z,GRID_TYPES["ROAD"])
                    else:
                        editor.placeBlock(i,WORLDSLICE.heightmaps["MOTION_BLOCKING"][(i,j-z)]-1,j-z, "grass_path")
                        print("Building road at", i, j-z)
                        if grid.is_type(i,j-z,GRID_TYPES["ROAD"]):
                            break
                        grid.set_grid(i,j-z,GRID_TYPES["ROAD"])

def buildRoadForAstar(path,x,y,editor, WORLDSLICE, grid):
    for i in range(len(path)):
        x += path[i][0]
        y += path[i][1]
        if grid.is_type(x,y,GRID_TYPES["ROAD"]):
            continue
        if path[i][0] == 0 :
            block = editor.getBlock(x-1,WORLDSLICE.heightmaps["MOTION_BLOCKING_NO_LEAVES"][(x-1,y)]-1,y)
            road = "oak_planks" if block == "minecraft:water" else "grass_path"
            grid.set_grid(x-1,y,GRID_TYPES["ROAD"])
            editor.placeBlock(x-1,WORLDSLICE.heightmaps["MOTION_BLOCKING"][(x-1,y)]-1,y, road)
            block = editor.getBlock(x+1,WORLDSLICE.heightmaps["MOTION_BLOCKING_NO_LEAVES"][(x+1,y)]-1,y)
            road = "oak_planks" if block == "minecraft:water" else "grass_path"
            grid.set_grid(x+1,y,GRID_TYPES["ROAD"])
            editor.placeBlock(x+1,WORLDSLICE.heightmaps["MOTION_BLOCKING"][(x+1,y)]-1,y, road)
        else:
            block = editor.getBlock(x,WORLDSLICE.heightmaps["MOTION_BLOCKING_NO_LEAVES"][(x,y-1)]-1,y-1)
            road = "oak_planks" if block == "minecraft:water" else "grass_path"
            grid.set_grid(x,y-1,GRID_TYPES["ROAD"])
            editor.placeBlock(x,WORLDSLICE.heightmaps["MOTION_BLOCKING"][(x,y-1)]-1,y-1, road)
            block = editor.getBlock(x,WORLDSLICE.heightmaps["MOTION_BLOCKING_NO_LEAVES"][(x,y+1)]-1,y+1)
            road = "oak_planks" if block == "minecraft:water" else "grass_path"
            grid.set_grid(x,y+1,GRID_TYPES["ROAD"])
            editor.placeBlock(x,WORLDSLICE.heightmaps["MOTION_BLOCKING"][(x,y+1)]-1,y+1, road)
        grid.set_grid(x,y,GRID_TYPES["ROAD"])
        editor.placeBlock(x,WORLDSLICE.heightmaps["MOTION_BLOCKING"][(x,y)]-1,y, road)




def buildRoadAroundbuildings(editor, WORLDSLICE, grid,building_x,building_z,width,depth):
    print("Started building road around town hall")
    start_x = building_x+build_area.begin.x-1
    start_z = building_z+build_area.begin.z-1
    end_x = start_x + width+2
    end_z = start_z + depth+2
    for i in range(start_x, end_x):
        for j in range(2):
            block = editor.getBlock((i,WORLDSLICE.heightmaps["MOTION_BLOCKING_NO_LEAVES"][(i,start_z+j)]-1,start_z+j))
            road = "oak_planks" if block == "minecraft:water" else "dirt_path"
            editor.placeBlock((i,WORLDSLICE.heightmaps["MOTION_BLOCKING"][(i,start_z+j)]-1,start_z+j), Block(road))
            block = editor.getBlock((i,WORLDSLICE.heightmaps["MOTION_BLOCKING_NO_LEAVES"][(i,end_z-j)]-1,end_z-j))
            road = "oak_planks" if block == "minecraft:water" else "dirt_path"
            editor.placeBlock((i,WORLDSLICE.heightmaps["MOTION_BLOCKING"][(i,end_z-j)]-1,end_z-j), Block(road))
            grid.set_grid(i,start_z+j,GRID_TYPES["ROAD"])
            grid.set_grid(i,end_z-j,GRID_TYPES["ROAD"])
    
    for i in range(start_z, end_z):
        for j in range(2):
            block = editor.getBlock((start_x+j,WORLDSLICE.heightmaps["MOTION_BLOCKING_NO_LEAVES"][(start_x+j,i)]-1,i))
            road = "oak_planks" if block == "minecraft:water" else "dirt_path"
            editor.placeBlock((start_x+j,WORLDSLICE.heightmaps["MOTION_BLOCKING"][(start_x+j,i)]-1,i), Block(road))
            block = editor.getBlock((end_x-j,WORLDSLICE.heightmaps["MOTION_BLOCKING_NO_LEAVES"][(end_x-j,i)]-1,i))
            road = "oak_planks" if block == "minecraft:water" else "dirt_path"
            editor.placeBlock((end_x-j,WORLDSLICE.heightmaps["MOTION_BLOCKING"][(end_x-j,i)]-1,i), Block(road))
            grid.set_grid(start_x+j,i,GRID_TYPES["ROAD"])
            grid.set_grid(end_x-j,i,GRID_TYPES["ROAD"])
    print("Finished building road around town hall")


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
    buildin_x = item['x']
    building_z = item['z']
    width = item['width']
    depth = item['depth']
    buildRoadAroundbuildings(editor, world_slice, grid, building_x, building_z,width,depth)
from collections import deque

from collections import deque
from typing import List, Tuple

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
        grid.set_grid(x,start_z,2)
        grid.set_grid(x,end_z-1,2)
        

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


def create_grid(build_area_size, draw_buildings, file_paths, build_area, editor, world_slice, bunker_height):
    grid=Grid(build_area_size.x, build_area_size.z)
    placed_buildings= place_or_get_buildings(draw_buildings, file_paths, build_area_size, build_area, editor,  100, grid,bunker_height)
    print(placed_buildings)
    # buildRoadAroundbuildings(editor, world_slice, grid,placed_buildings.,placed_buildings[0][1],placed_buildings[0][2],placed_buildings[0][3])
    for item in placed_buildings:
        building_x = item['x']
        building_z = item['z']
        width = item['width']
        depth = item['depth']
        buildRoadAroundbuildings(editor, world_slice, grid, building_x, building_z,width,depth)

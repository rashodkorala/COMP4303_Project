import sys
sys.path.append("setup_files")
import numpy as np
from gdpc import __url__, Editor, Block, geometry
from gdpc.exceptions import InterfaceConnectionError, BuildAreaNotSetError
from gdpc.vector_tools import addY
from buildArea_calc import *


""" #setting up build area and heightmap
editor = create_editor()
world_slice, build_rect, build_area = get_world_slice(editor)
heightmap = get_build_area(build_rect, world_slice, build_area)


#clearing the build area
print("flatten build area...")
flatten_area(heightmap, build_rect, editor, build_area) """


editor, world_slice, build_rect, build_area, heightmap = set_cleared_area()



# Place walls of stone bricks on the perimeter of the build area, following the curvature of the
# terrain.
print("Placing walls...")
for point in build_rect.outline:
    height = heightmap[tuple(point - build_rect.offset)]
    #building a wall
    for y in range(height, height+9):
        # Place the first layer of blocks
        editor.placeBlock(addY(point, y), Block("cobblestone")) 
    




#nbt imports
#change python path so that nbt files can be recognized 
sys.path[0] = sys.path[0].removesuffix('\\biomes\\test')
from build_nbt_structure import *


filepath = "biomes\grass\grass_structures\grass_townhall.nbt"
#create nbt structure
create_nbt_structure(filepath, editor, build_area)

#maybe make a list of all nbt structures and loop throught them each

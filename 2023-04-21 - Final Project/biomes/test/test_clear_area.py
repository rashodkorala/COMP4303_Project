import sys
sys.path.append("setup_files")
import numpy as np
from gdpc import __url__, Editor, Block, geometry
from gdpc.exceptions import InterfaceConnectionError, BuildAreaNotSetError
from gdpc.vector_tools import addY
from buildArea_calc import *
from clearArea import *
from gdpc import WorldSlice as ws

#setting up build area and heightmap
editor = create_editor()
world_slice, build_rect, build_area = get_world_slice(editor)
heightmap = get_build_area(build_rect, world_slice, build_area)

# Starx, Stary, Starz , Endx, Endy, Endz = 
# world_slice = ws(rect=(Starx, Starz, Endx+1, Endz+1))



#clearing the build area
print("Clearing build area...")
clear_surface(heightmap, build_rect, editor, world_slice)   
print("flatten build area...")
flatten_area(heightmap, build_rect, editor, build_area)
print("build_area_size:",build_area.size)
print("build_area_begin:",build_area.begin)



# Place walls of stone bricks on the perimeter of the build area, following the curvature of the
# terrain.
""" print("Placing walls...")

for point in build_rect.inner:
    
    height = heightmap[tuple(point - build_rect.offset)]

    #building a wall
    
    for y in range(height, height+9):
        # Place the first layer of blocks
        editor.placeBlock(addY(point, y), Block("air")) """
    
        
#!/usr/bin/env python3

"""
Load and use a world slice.
"""

import sys

import numpy as np

from gdpc import __url__, Editor, Block, geometry
from gdpc.exceptions import InterfaceConnectionError, BuildAreaNotSetError
from gdpc.vector_tools import addY

sys.path.append("setup_files/buildArea_calc.py")
from buildArea_calc import *



editor = create_editor()
world_slice, build_rect, build_area = get_world_slice(editor)
heightmap = get_build_area(build_rect, world_slice)

# Place walls of stone bricks on the perimeter of the build area, following the curvature of the
# terrain.

print("Placing walls...")

for point in buildRect.outline:
    
    height = heightmap[tuple(point - buildRect.offset)]

    #building a wall
    
    for y in range(height, height + 7):
        # Place the first layer of blocks
        editor.placeBlock(addY(point, y), Block("mossy_stone_bricks"))
        
        # Place the second layer of blocks
        editor.placeBlock(addY(point+1, height+8), Block("mossy_stone_bricks"))
    
        


geometry.placeCylinder(editor,addY(buildRect.center, height-1), 55 , 1, Block("grass_block"))

#placing the beacon
print("Placing beacon...")
geometry.placeCylinder(editor,addY(buildRect.center, height), 5 , 1, Block("emerald_block"))
editor.placeBlock(addY(buildRect.center, height+1), Block("beacon"))
editor.placeBlock(addY(buildRect.center, height+2), Block("yellow_stained_glass"))

#build the bamboo grove
print("Placing bamboo grove...")

geometry.placeCylinder(editor,addY(buildRect.center, height), 41 , 1, Block("dark_oak_log"), tube=True)
geometry.placeCylinder(editor,addY(buildRect.center, height+1), 41 , 1, Block("stone_brick_slab"), tube=True)
geometry.placeCylinder(editor,addY(buildRect.center, height), 47 , 1, Block("dark_oak_log"), tube=True)
geometry.placeCylinder(editor,addY(buildRect.center, height), 49 , 1, Block("stone_brick_slab"), tube=True)

for x in range(43,46, 2):
    geometry.placeCylinder(editor,addY(buildRect.center, height), x , 1, Block("water"), tube=True)

for m in range(7,36,2):
    geometry.placeCylinder(editor,addY(buildRect.center, height), m , 1, Block("bamboo"), tube=True)




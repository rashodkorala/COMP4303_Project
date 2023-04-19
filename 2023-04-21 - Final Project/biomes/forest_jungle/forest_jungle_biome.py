
import sys
sys.path.append("setup_files")
import numpy as np
from gdpc import __url__, Editor, Block, geometry
from gdpc.exceptions import InterfaceConnectionError, BuildAreaNotSetError
from gdpc.vector_tools import addY
from buildArea_calc import *
from clearArea import *


#setting up build area and heightmap
editor = create_editor()
world_slice, build_rect, build_area = get_world_slice(editor)
heightmap = get_build_area(build_rect, world_slice, build_area)




#clearing the build area
print("Clearing build area...")
clear_area(heightmap, build_rect, build_area, editor, world_slice)  


# Place walls of stone bricks on the perimeter of the build area, following the curvature of the
# terrain.
print("Placing walls...")

for point in build_rect.outline:
    
    height = heightmap[tuple(point - build_rect.offset)]

    #building a wall
    
    for y in range(height, height + 7):
        # Place the first layer of blocks
        editor.placeBlock(addY(point, y), Block("mossy_stone_bricks"))
        

        


geometry.placeCylinder(editor,addY(build_rect.center, height-1), 55 , 1, Block("grass_block"))

#placing the beacon
print("Placing beacon...")
geometry.placeCylinder(editor,addY(build_rect.center, height), 5 , 1, Block("emerald_block"))
editor.placeBlock(addY(build_rect.center, height+1), Block("beacon"))
editor.placeBlock(addY(build_rect.center, height+2), Block("yellow_stained_glass"))

#build the bamboo grove
print("Placing bamboo grove...")

geometry.placeCylinder(editor,addY(build_rect.center, height), 41 , 1, Block("dark_oak_log"), tube=True)
geometry.placeCylinder(editor,addY(build_rect.center, height+1), 41 , 1, Block("stone_brick_slab"), tube=True)
geometry.placeCylinder(editor,addY(build_rect.center, height), 47 , 1, Block("dark_oak_log"), tube=True)
geometry.placeCylinder(editor,addY(build_rect.center, height), 49 , 1, Block("stone_brick_slab"), tube=True)

for x in range(43,46, 2):
    geometry.placeCylinder(editor,addY(build_rect.center, height), x , 1, Block("water"), tube=True)

for m in range(7,36,2):
    geometry.placeCylinder(editor,addY(build_rect.center, height), m , 1, Block("bamboo"), tube=True)


import sys
sys.path[0] = sys.path[0].removesuffix('\\forest_jungle')
sys.path[0] = sys.path[0].removesuffix('\\biomes')



from structures.nbt.convert_nbt import convert_nbt
from structures.nbt.nbt_asset import NBTAsset
from structures.structure import Structure
from structures.transformation import Transformation
from gdpc.editor import Editor
from gdpc.block import Block
from palette.palette import Palette
from palette.palette_swap import palette_swap

structure = convert_nbt("C:/Users/vilak/Desktop/Folders/2022-2023/CS4303 Assignment files/COMP4303_Project/2023-04-21 - Final Project/biomes/grass/grass_structures/grass_tower.nbt")
for (pos, palette_index) in structure.blocks.items():
    block = structure.palette[palette_index]
    build_pos = build_area.begin + pos
    editor.placeBlock(position=build_pos, block=block.to_gdpc_block())
    print(build_pos, block.to_gdpc_block())


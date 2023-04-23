import sys
sys.path.append("setup_files")
import numpy as np
from gdpc import __url__, Editor, Block, geometry
from gdpc.exceptions import InterfaceConnectionError, BuildAreaNotSetError
from gdpc.vector_tools import addY
from buildArea_calc import *
from clearArea_calc import *
from gdpc import WorldSlice as ws

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
    



import sys
#sys.path[0] = sys.path[0].removesuffix('\\test') <- change this path
sys.path[0] = sys.path[0].removesuffix('\\biomes\\grass')

print(sys.path[0])
input("press to continue")
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
    build_pos = buildArea.begin + pos
    editor.placeBlock(position=build_pos, block=block.to_gdpc_block())
    print(build_pos, block.to_gdpc_block())



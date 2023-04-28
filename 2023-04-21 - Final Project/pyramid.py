#!/usr/bin/env python3

"""
Load and use a world slice.
"""

import sys

import numpy as np

from gdpc import __url__, Editor, Block, geometry
from gdpc.exceptions import InterfaceConnectionError, BuildAreaNotSetError
from gdpc.vector_tools import addY,Rect


# Create an editor object.
# The Editor class provides a high-level interface to interact with the Minecraft world.
editor = Editor()


# Check if the editor can connect to the GDMC HTTP interface.
try:
    editor.checkConnection()
except InterfaceConnectionError:
    print(
        f"Error: Could not connect to the GDMC HTTP interface at {editor.host}!\n"
        "To use GDPC, you need to use a \"backend\" that provides the GDMC HTTP interface.\n"
        "For example, by running Minecraft with the GDMC HTTP mod installed.\n"
        f"See {__url__}/README.md for more information."
    )
    sys.exit(1)


# Get the build area.
try:
    buildArea = editor.getBuildArea()
except BuildAreaNotSetError:
    print(
        "Error: failed to get the build area!\n"
        "Make sure to set the build area with the /setbuildarea command in-game.\n"
        "For example: /setbuildarea ~0 0 ~0 ~64 200 ~64"
        #~0 0 ~0 is the center of the build area.
        #~64 200 ~64 is the size of the build area. With 200 being the height. With ~ being the player.
    )
    sys.exit(1)


# Get a world slice.
#
# A world slice contains all kinds of information about a slice of the world, like blocks, biomes
# and heightmaps. All of its data is extracted directly from Minecraft's chunk format:
# https://minecraft.fandom.com/wiki/Chunk_format. World slices take a while to load, but accessing
# data from them is very fast.
#
# To get a world slice, you need to specify a rectangular XZ-area using a Rect object (the 2D
# equivalent of a Box). Box.toRect() is a convenience function that converts a Box to its XZ-rect.
#
# Note that a world slice is a "snapshot" of the world: any changes you make to the world after
# loading a world slice are not reflected by it.

print("Loading world slice...")
buildRect = buildArea.toRect()
worldSlice = editor.loadWorldSlice(buildRect)
print("World slice loaded!")




# Most of worldSlice's functions have a "local" and a "global" variant. The local variant expects
# coordinates relatve to the rect with which it was constructed, while the global variant expects
# absolute coorndates.


vec = addY(buildRect.center, 0)
print(f"Block at {vec}: {worldSlice.getBlock(vec - buildArea.offset)}")
print(f"Block at {vec}: {worldSlice.getBlockGlobal(vec)}")


# Heightmaps are an easy way to get the uppermost block at any coordinate. They are very useful for
# writing terrain-adaptive generator algorithms.
# World slices provide access to the heightmaps that Minecraft stores in its chunk format, so you
# get their computation for free.
#
# By default, world slices load the following four heightmaps:
# - "WORLD_SURFACE":             The top non-air blocks.
# - "MOTION_BLOCKING":           The top blocks with a hitbox or fluid.
# - "MOTION_BLOCKING_NO_LEAVES": Like MOTION_BLOCKING, but ignoring leaves.
# - "OCEAN_FLOOR":               The top non-air solid blocks.
#
# Heightmaps are loaded into 2D numpy arrays of Y coordinates.

print(f"Available heightmaps: {worldSlice.heightmaps.keys()}")

heightmap = worldSlice.heightmaps["MOTION_BLOCKING_NO_LEAVES"]

print(f"Heightmap shape: {heightmap.shape}")



# Place walls of stone bricks on the perimeter of the build area, following the curvature of the
# terrain.



# print("Placing walls...")

# for point in buildRect.outline:
#     height = heightmap[tuple(point - buildRect.offset)]
#     #building a wall

#     for y in range(height, height+1):
#         # Place the first layer of blocks
#         editor.placeBlock(addY(point, y), Block("ice"))
#         editor.placeBlock(addY(point, y+2), Block("blue_ice"))
#         editor.placeBlock(addY(point, y+3), Block("snow_block"))
#         editor.placeBlock(addY(point, y+4), Block("snow_block"))
#         editor.placeBlock(addY(point, y+5), Block("torch"))

# height = heightmap[tuple(point - buildRect.offset)]
#create a pyramid shape
# gemoetry.placeCylinder(editor: Editor,block: Union[Block, Sequence[Block]],axis=1, tube=False, hollow=False,replace: Optional[Union[str, List[str]]] = None):
# placeRect(editor: Editor, rect: Rect, y: int, block: Union[Block, Sequence[Block]], replace: Optional[Union[str, List[str]]] = None):
height = heightmap[tuple(buildRect.center - buildRect.offset)]
# geometry.placeCylinder(editor,addY(buildRect.center, height), 30 , 10, Block("dark_oak_planks"), tube=True)
# geometry.placeRect(editor, buildRect, height-1, Block("sandstone"))


# def print_pyramid(height,starting_height):
#     for i in range(height):
#         # Print spaces for each row
#         for j in range(height - i - 1):
#             print(" ", end="")

#         # Print the stars (or any other character) for each row
#         for k in range(2 * i + 1):
#            geometry.placeRect(editor, rect=Rect(i), starting_height+k, Block("dark_oak_planks"))

# print_pyramid(10,height)

""" def build_pyramid(editor, height, starting_pos, block_type):
    for y in range(height):
        for x in range(-y, y + 1):
            for z in range(-y, y + 1):
                if abs(x) == y or abs(z) == y:
                    position = starting_pos + np.array([x, y, z])
                    editor.placeBlock(position, block_type)

# Example usage
starting_position = addY(buildRect.center, height)
block_type = Block("sandstone")
pyramid_height = 40
# build_pyramid(editor, pyramid_height, starting_position, block_type)
print(buildRect._offset) """

""" def create_sandstone_floor(editor, block_type, size, starting_pos):
    for x in range(-size // 2, size // 2 + 1):
        for z in range(-size // 2, size // 2 + 1):
            position = starting_pos + np.array([x, 0, z])
            editor.placeBlock(position, block_type) """

import random
import numpy as np


block_array = ["orange_terracotta","lime_terracotta","red_terracotta","cut_sandstone"]
block_array1=["chiseled_red_sandstone","chiseled_sandstone"]
def create_initial_floor(width, height, block_array):
    return [[random.choice(block_array) for _ in range(width)] for _ in range(height)]

#add Celluar Automata to the floor
def count_neighbors(x, y, floor, block_type):
    neighbors = 0
    for dx in range(-1, 2):
        for dy in range(-1, 2):
            if dx == 0 and dy == 0:
                continue

            nx, ny = x + dx, y + dy

            if 0 <= nx < len(floor[0]) and 0 <= ny < len(floor):
                if floor[ny][nx] == block_type:
                    neighbors += 1

    return neighbors

def update_floor(floor, block_array, birth_limit, death_limit):
    new_floor = [[None for _ in range(len(floor[0]))] for _ in range(len(floor))]

    for y in range(len(floor)):
        for x in range(len(floor[0])):
            current_block_type = floor[y][x]
            same_type_neighbors = count_neighbors(x, y, floor, current_block_type)

            if same_type_neighbors <= death_limit:
                other_block_types = [block_type for block_type in block_array if block_type != current_block_type]
                possible_births = {block_type: count_neighbors(x, y, floor, block_type) for block_type in other_block_types}

                for block_type, count in possible_births.items():
                    if count >= birth_limit:
                        new_floor[y][x] = block_type
                        break
                else:
                    new_floor[y][x] = current_block_type
            else:
                new_floor[y][x] = current_block_type

    return new_floor

#rule 90
def update_floor_rule_90(floor, block_array):
    new_floor = [[None for _ in range(len(floor[0]))] for _ in range(len(floor))]

    for y in range(len(floor)):
        for x in range(len(floor[0])):
            left_neighbor = floor[y][x - 1] if x > 0 else floor[y][-1]
            right_neighbor = floor[y][x + 1] if x < len(floor[0]) - 1 else floor[y][0]

            if left_neighbor == right_neighbor:
                new_floor[y][x] = floor[y][x]
            else:
                new_floor[y][x] = [block for block in block_array if block != floor[y][x]][0]

    return new_floor

#inner pyramid
def build_inner_pyramid(editor, size, block_type, pyramid_starting_pos, bl_array=block_array):
    for y in range(size):
        for x in range(-size + y + 1, size - y):
            for z in range(-size + y + 1, size - y):
                position = pyramid_starting_pos + np.array([x, y, z])
                rand=random.randint(0,100)
                if rand<50:
                    editor.placeBlock(position, block_type)
                else:
                    editor.placeBlock(position, Block("chiseled_red_sandstone"))
                if (abs(x) == size - y - 1 or abs(z) == size - y - 1 ):
                    editor.placeBlock(position+np.array([0,1,0]), Block("torch"))

#outer pyramid       
def build_inverted_pyramid(editor, size,pyramid_starting_pos,grid,grid_local):
    bl_array=block_array
    birth_limit = 2
    death_limit = 1
    door_size = 3
    # floor= create_initial_floor(size, size,bl_array)
    floor= create_initial_floor(size, size,bl_array)
    wall=create_initial_floor(size, size,block_array1)
    for y in range(size):
        floor = update_floor_rule_90(floor, bl_array)
        wall=update_floor(wall, block_array1, birth_limit, death_limit)
        for x in range(-size + y + 1, size - y):
            for z in range(-size + y + 1, size - y):
                position = pyramid_starting_pos + np.array([x, y, z])
                CA_block_type=Block(floor[x][z])
                CA_block_type_wall=Block(wall[x][z])
                if (abs(x) == size - y - 1 or abs(z) == size - y - 1 ):
                    editor.placeBlock(position, CA_block_type_wall)
                elif y == 0:
                    local_pos=grid_local+np.array([x, y, z])
                    grid.set_grid(local_pos[0],local_pos[2],1)
                    editor.placeBlock(position, CA_block_type)
                else:
                    editor.placeBlock(position, Block("air"))

    
        """ editor.placeBlock(starting_pos + np.array([height-2, 1, 0]), Block("spruce_door[facing=west ,half=lower,hinge=left]"))
        editor.placeBlock(starting_pos + np.array([height-2, 1, 1]), Block("air"))
        editor.placeBlock(starting_pos + np.array([height-2, 1, 0]), Block("air"))
        editor.placeBlock(starting_pos + np.array([height-2, 1, -1]), Block("air"))
        editor.placeBlock(starting_pos + np.array([height-3, 2, 1]), Block("air"))
        editor.placeBlock(starting_pos + np.array([height-3, 2, 0]), Block("air"))
        editor.placeBlock(starting_pos + np.array([height-3, 2, -1]), Block("air"))
        editor.placeBlock(starting_pos + np.array([height-4, 3, 1]), Block("air"))
        editor.placeBlock(starting_pos + np.array([height-4, 3, 0]), Block("air"))
        editor.placeBlock(starting_pos + np.array([height-4, 3, -1]), Block("air")) """
    for y in range(1,door_size+1):
        for x in range(door_size):
            for z in range(-1,door_size-1):
                if x==1:
                    local_pos=grid_local+np.array([size-2-x, y, z])
                    grid.set_grid(local_pos[0],local_pos[2],3)
                editor.placeBlock(starting_pos + np.array([size-2-x, y, z]), Block("air"))
    
pyramid_size = 14#random.randint(10, 14)
print(pyramid_size)
starting_pos = buildArea.begin
pyramid_block_type = Block("sandstone")
#choose two random numbers between 0 and 4
rand1=random.randint(0, 4)
while True:
    rand2=random.randint(0, 4)
    if rand1!=rand2:
        break
print(rand1,rand2)

random_block_array=[block_array[rand1],block_array[rand2]]

build_inverted_pyramid(editor,pyramid_size, pyramid_block_type, starting_pos,random_block_array)
pyramid_size = pyramid_size - pyramid_size//2 - pyramid_size//4
pyramid_block_type = Block("chiseled_sandstone")

build_inner_pyramid(editor, pyramid_size, pyramid_block_type, starting_pos+np.array([0,pyramid_size//2-1,0]))
  


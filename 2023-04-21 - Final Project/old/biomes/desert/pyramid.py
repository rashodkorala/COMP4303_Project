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



print("Placing walls...")

for point in buildRect.outline:
    height = heightmap[tuple(point - buildRect.offset)]
    #building a wall

    for y in range(height, height+1):
        # Place the first layer of blocks
        editor.placeBlock(addY(point, y), Block("ice"))
        editor.placeBlock(addY(point, y+2), Block("blue_ice"))
        editor.placeBlock(addY(point, y+3), Block("snow_block"))
        editor.placeBlock(addY(point, y+4), Block("snow_block"))
        editor.placeBlock(addY(point, y+5), Block("torch"))

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

def build_pyramid(editor, height, starting_pos, block_type):
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
print(buildRect._offset)

def create_sandstone_floor(editor, y, block_type):
    startx=buildRect._offset[0]-13
    startz=buildRect._offset[1]-13
    endx=buildRect._offset[0]+buildRect._size[0]+13
    endz=buildRect._offset[1]+buildRect._size[1]+13
    for x in range(startx, endx):
        for z in range(startz, endz):
            position = np.array([x, y, z])
            editor.placeBlock(position, block_type)

# Example usage
# Create sandstone floor
floor_y = height - 1
floor_block_type = Block("sandstone")
# create_sandstone_floor(editor, buildRect, floor_y, floor_block_type)

def build_inverted_pyramid(editor, height, starting_pos, block_type):
    for y in range(height):
        for x in range(-height + y + 1, height - y):
            for z in range(-height + y + 1, height - y):
                if abs(x) == height - y - 1 or abs(z) == height - y - 1:
                    position = starting_pos + np.array([x, y, z])
                    editor.placeBlock(position, block_type)

# Example usage
starting_position = addY(buildRect.center, height)
block_type = Block("sandstone")
pyramid_height = 20
# build_inverted_pyramid(editor, pyramid_height, starting_position, block_type)
def build_hollow_inverted_pyramid(editor, length, width, height, starting_pos, block_type, line_height, size_reduction):
    for y in range(0, height * line_height, line_height):
        for x in range(-length // 2 + y // line_height * size_reduction + 2, length // 2 - y // line_height * size_reduction):
            for z in range(-width // 2 + y // line_height * size_reduction + 2, width // 2 - y // line_height * size_reduction):
                for i in range(line_height):
                    if (
                            x == -length // 2 + y // line_height * size_reduction + 2
                            or x == length // 2 - y // line_height * size_reduction - 1
                            or z == -width // 2 + y // line_height * size_reduction + 2
                            or z == width // 2 - y // line_height * size_reduction - 1
                            or i == line_height - 1

                        ):
                            position = starting_pos + np.array([x, y + i, z])
                            editor.placeBlock(position, block_type)

                    
                
                    




# Example usage
# Create sandstone floor
floor_y = (height * 4) - 1
floor_block_type = Block("cut_sandstone")
# create_sandstone_floor(editor, floor_y, floor_block_type)

# Build filled inverted pyramid with customizable length, width, and height
starting_position = addY(buildRect.center, height)
block_type = Block("cut_sandstone")
length, width, heightA = 20, 20, 20



# geometry.placeCylinder(editor, addY(buildRect.center, height), 8 , 18, Block("cracked_polished_blackstone_bricks"), tube=True)
# create_sandstone_floor(editor, buildArea.begin.y, floor_block_type)
# build_hollow_inverted_pyramid(editor, length, width, heightA, starting_position, block_type, line_height=1, size_reduction=1)
# build_inverted_pyramid(editor, pyramid_height, starting_position, block_type)
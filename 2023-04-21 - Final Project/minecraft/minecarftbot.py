#!/usr/bin/env python3

"""
Load and use a world slice.
"""

from random import randint
import sys

import numpy as np

from gdpc import __url__, Editor, Block
from gdpc.exceptions import InterfaceConnectionError, BuildAreaNotSetError
from gdpc.vector_tools import addY
from gdpc import WorldSlice as ws
from gdpc import geometry as geo


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

vec = addY(buildRect.center, 30)
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

localCenter = buildRect.size // 2
# When indexing a numpy array with a vector, you need to convert to a tuple first.
centerHeight = heightmap[tuple(localCenter)]
centerTopBlock = worldSlice.getBlock(addY(localCenter, centerHeight - 1))
print(f"Top block at the center of the build area: {centerTopBlock}")

print(f"Average height: {int(np.mean(heightmap))}")


# Place walls of stone bricks on the perimeter of the build area, following the curvature of the
# terrain.

# print("Placing walls...")

# for point in buildRect.outline:
#     height = heightmap[tuple(point - buildRect.offset)]

#     for y in range(height, height + 5):
#         editor.placeBlock(addY(point, y), Block("stone_bricks"))





print("Cleaning the area...")
bottom = worldSlice.heightmaps["MOTION_BLOCKING_NO_LEAVES"]
top = worldSlice.heightmaps["WORLD_SURFACE"]
# print(bottom)
# print(top)
# STARTX, STARTY, STARTZ, ENDX, ENDY, ENDZ = editor.getBuildArea() 

def clearbuildArea():
    for x in range(buildRect._offset[0], buildRect._offset[0] + buildRect.size[0]):
        for z in range(buildRect._offset[1], buildRect._offset[1] + buildRect.size[1]):
            start = bottom[(x - buildRect._offset[0], z - buildRect._offset[1])]
            end = top[(x - buildRect._offset[0], z - buildRect._offset[1])]
            # block = editor.getBlock((x, start - 1, z))
            block = editor.getBlock((x, start - 1, z)) 
            while ("log" in block.id or "leaves" in block.id or "mushroom" in block.id ) and start > 0:
                start = start - 1
                block = editor.getBlock((x, start - 1, z))
            if "dirt" in block.id:
                editor.placeBlock((x, start - 1, z), Block("grass_block"))
            for y in range(start, end):
                editor.placeBlock((x, y, z), Block("air")) 
            # if "air" in block.id: w
            #     continue
            # else:
            #     # editor.placeBlock((x, start - 1, z), Block("grass_block"))
            #     for y in range(start, end):
            #         editor.placeBlock((x, y, z), Block("air"))    
    print("Done!") 


def build_wall():
    for point in buildRect.outline:
        height = heightmap[tuple(point - buildRect.offset)]

        for y in range(height, height + 5):
            editor.placeBlock(addY(point, y), Block("stone_bricks"))
    print("Done!")

gravity_affected_blocks = ["sand", "red_sand", "gravel", "anvil", "concrete_powder", "scaffolding"]




def is_gravity_affected(block_id):
    return any(item in block_id for item in gravity_affected_blocks)
def cleanarea():
    print("Placing the flat floor...")

    floor_block = Block("stone_bricks")

# Calculate the average height
    min_height = heightmap.min()
    max_height = heightmap.max()
    average_height = int(np.mean(heightmap))

    for x in range(buildRect._offset[0], buildRect._offset[0] + buildRect.size[0]):
        for z in range(buildRect._offset[1], buildRect._offset[1] + buildRect.size[1]):
            for y in range(max_height, min_height - 1, -1):
                # current_block = editor.getBlock((x, y, z))
                # editor.placeBlock((x, y, z), Block("air"))
                # if is_gravity_affected(current_block.id):
                #     below_y = y - 1
                #     below_block = editor.getBlock((x, below_y, z))
                #     while is_gravity_affected(below_block.id):
                #         editor.placeBlock((x, below_y, z), Block("air"))
                #         below_y -= 1
                #         below_block = editor.getBlock((x, below_y, z))
                editor.placeBlock((x, y, z), Block("air"))

    


# build_wall() 
# clearbuildArea()





            
cleanarea()
build_wall()

        


            
    
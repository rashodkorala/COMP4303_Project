#!/usr/bin/env python3

"""
Load and use a world slice.
"""

import sys

import numpy as np

from gdpc import __url__, Editor, Block, geometry
from gdpc.exceptions import InterfaceConnectionError, BuildAreaNotSetError
from gdpc.vector_tools import addY


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
    
    for y in range(height, height + 1):
        # Place the first layer of blocks
        editor.placeBlock(addY(point, y), Block("mossy_stone_bricks"))
        
        # Place the second layer of blocks
        #editor.placeBlock(addY(point+1, height+8), Block("mossy_stone_bricks"))
     







#importing structures
from barracks import *
from archer_tower import *
from townhall import *
from bunker import *
from center_structures import *
import random


# Call the function to create the townhall
starting_pos = buildArea.begin
wall_block_type = 'stone_bricks'
roof_block_type = 'stone'
floor_block_type = 'oak_planks'
window_block_type = 'glass_pane'
staircase_block_type = 'oak_stairs'


# Set the starting position and block types
starting_pos = buildArea.begin+np.array([25,0,25])
bunker_wall = 'oak_planks'
bunker_roof = 'spruce_planks'
bunker_floor = 'oak_planks'

# Call the function to create the wooden barrack in Minecraft
rotation_angle = 90

# bunker(editor, starting_pos, wall_block_type, roof_block_type, floor_block_type, rotation_angle)

# townhall(editor, starting_pos, wall_block_type, roof_block_type, floor_block_type, window_block_type, staircase_block_type)


height = 4 
block_type = 'stone_bricks'



buildings_list = [barracks(editor, starting_pos), 
                    archer_tower(editor, starting_pos, block_type, height), 
                    townhall(editor, starting_pos, wall_block_type, roof_block_type, 
                            floor_block_type, window_block_type, staircase_block_type), 
                    bunker(editor, starting_pos, bunker_wall, bunker_roof, 
                            bunker_floor, rotation_angle)]



for building, kwargs in buildings_list:


    x = random.randint(0, buildArea.size.x)
    z = random.randint(0,  buildArea.size.z)

    starting_pos = buildArea.begin + [x, 0, z]

    building(editor, starting_pos, **kwargs)
    
    



    


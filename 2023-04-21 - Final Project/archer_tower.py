
"""
Load and use a world slice.
"""

import sys
import time
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


def create_archer_tower(editor, starting_pos, wall_block_type, floor_block_type):
    base_length = 12
    base_width = 12
    tower_length = 8
    tower_width = 8
    wall_height = 10
    battlement_height = 2
    num_floors = 3

    # Create base
    for x in range(base_length):
        for z in range(base_width):
            position = starting_pos + np.array([x, 0, z])
            editor.placeBlock(position, Block(wall_block_type))

    # Create tower walls
    for floor in range(num_floors):
        for x in range(tower_length):
            for y in range(wall_height):
                for z in range(tower_width):
                    if x == 0 or x == tower_length - 1 or z == 0 or z == tower_width - 1:
                        position = starting_pos + np.array([x + 2, 1 + floor * (wall_height + 1) + y, z + 2])
                        editor.placeBlock(position, Block(wall_block_type))

        # Create tower floors
        for x in range(tower_length):
            for z in range(tower_width):
                position = starting_pos + np.array([x + 2, 1 + floor * (wall_height + 1), z + 2])
                editor.placeBlock(position, Block(floor_block_type))

    # Create battlements
    for x in range(tower_length):
        for y in range(battlement_height):
            for z in range(tower_width):
                if (x == 0 or x == tower_length - 1 or z == 0 or z == tower_width - 1) and (y == 0 or (x + y) % 2 == 0):
                    position = starting_pos + np.array([x + 2, 1 + num_floors * (wall_height + 1) + y, z + 2])
                    editor.placeBlock(position, Block(wall_block_type))

# Set the starting position and block types
starting_pos = np.array([0, 0, 0])
wall_block_type = 'stone_bricks'
floor_block_type = 'stone_bricks'

# Call the function to create the archer tower in Minecraft
create_archer_tower(editor, starting_pos, wall_block_type, floor_block_type)

#!/usr/bin/env python3

"""
Load and use a world slice.
"""

import random
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
""" def build_fishing_hut(editor, starting_pos, hut_size):
    # Build the base and walls
    for x in range(-hut_size, hut_size + 1):
        for z in range(-hut_size, hut_size + 1):
            for y in range(4):
                if y == 0:
                    editor.placeBlock(starting_pos + np.array([x, y, z]), Block("oak_planks"))
                elif x in (-hut_size, hut_size) or z in (-hut_size, hut_size):
                    editor.placeBlock(starting_pos + np.array([x, y, z]), Block("oak_log"))
                else:
                    editor.placeBlock(starting_pos + np.array([x, y, z]), Block("air"))

    # Add a roof (not shown in this example)
    for y in range(4, 4 + hut_size + 1):
        for x in range(-hut_size - 1, hut_size + 2):
            for z in range(-hut_size - 1, hut_size + 2):
                if z == -hut_size - 1 or z == hut_size + 1:
                    distance_from_edge = abs(y - 4)
                    if abs(x) <= hut_size - distance_from_edge:
                        editor.placeBlock(starting_pos + np.array([x, y, z]), Block("oak_stairs", {"facing": "north" if z < 0 else "south"}))


    # Place a door
    editor.placeBlock(starting_pos + np.array([-hut_size, 1, 0]), Block("oak_door", {"facing": "west", "half": "lower"}))

    # Add windows (not shown in this example)
    ...

    # Build a dock or pier
    for x in range(-hut_size - 1, hut_size + 2):
        for z in range(2 * hut_size + 1, 2 * hut_size + 4):
            if z == 2 * hut_size + 1:
                editor.placeBlock(starting_pos + np.array([x, 0, z]), Block("oak_log"))
            else:
                editor.placeBlock(starting_pos + np.array([x, 0, z]), Block("oak_planks"))

    # Add interior elements
    editor.placeBlock(starting_pos + np.array([0, 1, 0]), Block("crafting_table"))
    editor.placeBlock(starting_pos + np.array([1, 1, 0]), Block("chest"))
    editor.placeBlock(starting_pos + np.array([-1, 1, 0]), Block("furnace"))

    # Add decorative elements (not shown in this example)
    ...

# Build a fishing hut with a specified size
starting_pos = buildArea.begin+np.array([0, 0, 0])
build_fishing_hut(editor, starting_pos, hut_size=3) """


worldSlice.heightmaps["OCEAN_FLOOR"] = heightmap

buildArea.begin = buildArea.begin + np.array([0, 0, 0])
print(heightmap[0, 0])


# editor.placeBlock(buildArea.begin + np.array(w[0, 0, 0]), Block("oak_planks"))

def is_near_water(editor, starting_pos, check_radius,heightmap):
    water_count = 0
    total_blocks = 0

    for x in range(-check_radius, check_radius + 1):
        for y in range(-check_radius, check_radius + 1):
            for z in range(-check_radius, check_radius + 1):
                total_blocks += 1
                block = editor.getBlock(starting_pos + np.array([x, y, z]))
                if block.name == "water":
                    water_count += 1

    # Calculate the percentage of water blocks in the surrounding area
    water_percentage = water_count / total_blocks

    # Consider the building near or on water if more than a certain percentage of blocks are water
    if water_percentage > 0.2:
        return True
    else:
        return False


# Check if the building is near or on water
near_water = is_near_water(editor, starting_pos, check_radius=10)

if near_water:
    print("The building is near or on water.")
else:
    print("The building is not near or on water.")

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

height=10

import numpy as np

import math

def rotate_point(point, axis, angle):
    angle = math.radians(angle)
    cos_angle = math.cos(angle)
    sin_angle = math.sin(angle)

    rotation_matrix = np.zeros((3, 3))

    if axis == 'x':
        rotation_matrix[0] = [1, 0, 0]
        rotation_matrix[1] = [0, cos_angle, -sin_angle]
        rotation_matrix[2] = [0, sin_angle, cos_angle]
    elif axis == 'y':
        rotation_matrix[0] = [cos_angle, 0, sin_angle]
        rotation_matrix[1] = [0, 1, 0]
        rotation_matrix[2] = [-sin_angle, 0, cos_angle]
    elif axis == 'z':
        rotation_matrix[0] = [cos_angle, -sin_angle, 0]
        rotation_matrix[1] = [sin_angle, cos_angle, 0]
        rotation_matrix[2] = [0, 0, 1]
    else:
        raise ValueError("Invalid rotation axis")

    return np.matmul(rotation_matrix, point)


def build_igloo(editor, center_pos, block_type, radius, rotation_axis=None, rotation_angle=0):
    for x in range(-radius, radius + 1):
        for y in range(-radius, radius + 1):
            for z in range(-radius, radius + 1):
                local_pos = np.array([x, y, z])
                if rotation_axis:
                    local_pos = rotate_point(local_pos, rotation_axis, rotation_angle)
                position = center_pos + local_pos
                position = position.astype(int)  # Convert the position to integers
                distance_from_center = np.linalg.norm(local_pos)

                # Create the outer shell of the igloo
                if radius - 1 <= distance_from_center <= radius:
                    editor.placeBlock(position, Block(block_type))

                # Hollow out the inside of the igloo
                elif distance_from_center < radius - 1:
                    editor.placeBlock(position, Block("air"))

                # Create a floor using the same block type as the igloo
                elif distance_from_center <= radius and y == -radius:
                    editor.placeBlock(position, Block(block_type))

# Call the build_igloo() function to create an igloo rotated around the Y-axis by 45 degrees
center_pos = buildArea.begin+np.array([0, 0, 0])
build_igloo(editor, center_pos, "snow_block", 5, rotation_axis='z', rotation_angle=90)
center_pos = buildArea.begin+np.array([10, 0, 10])
build_igloo(editor, center_pos, "snow_block", 7, rotation_axis='x', rotation_angle=270)


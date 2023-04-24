
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

print(f"Heightmap shape: {heightmap.shape}")
def make_roof(editor, length, width, height, starting_pos, block_type, line_height, size_reduction):
    for y in range(0, height * line_height, line_height):
        for x in range(-length // 2 + y // line_height * size_reduction + 2, length // 2 - y // line_height * size_reduction):
            for z in range(-width // 2 + y // line_height * size_reduction + 2, width // 2 - y // line_height * size_reduction):
                for i in range(line_height):
                    is_edge = (
                        x == -length // 2 + y // line_height * size_reduction + 2
                        or x == length // 2 - y // line_height * size_reduction - 1
                        or z == -width // 2 + y // line_height * size_reduction + 2
                        or z == width // 2 - y // line_height * size_reduction - 1
                    )

                    if (is_edge and i == line_height - 1) or (i == line_height - 1 and (x == -length // 2 + y // line_height * size_reduction + 2 or x == length // 2 - y // line_height * size_reduction - 1 or z == -width // 2 + y // line_height * size_reduction + 2 or z == width // 2 - y // line_height * size_reduction - 1)):
                        position = starting_pos + np.array([x, y + i, z])
                        editor.placeBlock(position, Block(block_type))
                    
                    else:
                        position = starting_pos + np.array([x, y + i, z])
                        editor.placeBlock(position, Block("minecraft:air"))



def make_townhall(editor, starting_pos, wall_block_type, roof_block_type, floor_block_type, window_block_type, staircase_block_type):
    # Define dimensions and parameters
    length = 20
    width = 10
    wall_height = 10
    roof_height = 5
    line_height = 1
    size_reduction = 1
    """
    # Create walls
    for x in range(length):
        for y in range(2 * wall_height):
            for z in range(width):
                if x == 0 or x == length - 1 or z == 0 or z == width - 1 or (y == wall_height and (x != 0 and x != length - 1 and z != 0 and z != width - 1)):
                    position = starting_pos + np.array([x, y, z])
                    editor.placeBlock(position, Block(wall_block_type))
                else:
                    position = starting_pos + np.array([x, y, z])
                    editor.placeBlock(position, Block("minecraft:air"))

    # Create floors
    for x in range(1, length - 1):
        for y in range(0, 2 * wall_height-2 , wall_height):
            for z in range(1, width - 1):
                position = starting_pos + np.array([x, y, z])
                editor.placeBlock(position, Block(floor_block_type))

    # Create windows
    window_height = 2
    window_width = 2
    for y in range(1, 2 * wall_height, wall_height - window_height):
        for x in range(1, length - 1, window_width + 1):
            for z in range(1, width - 1, window_width + 1):
                if x + window_width < length - 1 and z + window_width < width - 1:
                    for i in range(window_width):
                        for j in range(window_height):
                            position = starting_pos + np.array([x + i-1, y + j, 0])
                            editor.placeBlock(position, Block(window_block_type))

    # Create roof
    roof_starting_pos = starting_pos + np.array([length // 2 - 1, 2 * wall_height - 1, width // 2 - 1])
    make_roof(editor, length + 3, width + 4, roof_height + 4, roof_starting_pos, roof_block_type, line_height, size_reduction)

    # Create entrance
    door_height = 3
    door_width = 2
    door_start_x = (length - door_width) // 2
    door_start_z = 0
    for x in range(door_start_x, door_start_x + door_width):
        for y in range(door_height):
            position = starting_pos + np.array([x, y+1, door_start_z])
            editor.placeBlock(position, Block('air'))


 """
    # Create staircase
    staircase_height = wall_height
    staircase_width = wall_height
    staircase_start_x = (length - staircase_width) // 2
    staircase_start_z = (width - staircase_width) // 2
    for x in range(staircase_start_x, staircase_start_x + staircase_width):
        for y in range(staircase_height):
            for z in range(staircase_start_z, staircase_start_z + staircase_width):
                if x == staircase_start_x or x == staircase_start_x + staircase_width - 1 or z == staircase_start_z or z == staircase_start_z + staircase_width - 1:
                    position = starting_pos + np.array([x, y, z])
                    editor.placeBlock(position, Block(staircase_block_type))
                else:
                    position = starting_pos + np.array([x, y, z])
                    editor.placeBlock(position, Block("minecraft:air"))


# Call the function to create the townhall
starting_pos = buildArea.begin
wall_block_type = 'stone_bricks'
roof_block_type = 'stone'
floor_block_type = 'oak_planks'
window_block_type = 'glass_pane'
staircase_block_type = 'oak_stairs'
# make_townha ll(editor, starting_pos, wall_block_type, roof_block_type, floor_block_type, window_block_type, staircase_block_type)


def create_pyramid_and_reflection_in_xz_plane(editor, starting_pos, block_type, height, building_h=20):
    # Build the pyramid
    for y in range(building_h):
        for i in range(height):
            for j in range(-height + i + 1  , height - i):
                if j == -height + i + 1 or j == height - i - 1:
                    position = starting_pos + np.array([j, y, i])
                    editor.placeBlock(position, Block(block_type))
        
    # Build the reflection of the pyramid
        for i in range(height):
            for j in range(-height + i + 1, height - i):
                if j == -height + i + 1 or j == height - i - 1:
                    position = starting_pos + np.array([j, y, -i])
                    editor.placeBlock(position, Block(block_type))
    starting_pos[1]=starting_pos[1]+building_h
    for y in range(10):
        for i in range(height-y):
            for j in range(-height + i + 1+y, height - i-y):
                if j == -height + i + 1+y or j == height - i - 1-y:
                    position = starting_pos + np.array([j, y, i])
                    editor.placeBlock(position, Block(block_type))

    # Build the reflection of the pyramidw 
        for i in range(height-y):
            for j in range(-height + i + 1+ y, height - i-y):
                if j == -height + i + 1+y or j == height - i - 1-y:
                    position = starting_pos + np.array([j, y, -i])
                    editor.placeBlock(position, Block(block_type))

    #add a enternce
    

# Set the height of the pyramid
height = 8
starting_pos =buildArea.begin+np.array([0,0,0])
block_type = 'stone_bricks'

# Call the function to create the pyramid and its reflection in Minecraft
create_pyramid_and_reflection_in_xz_plane(editor, starting_pos, block_type, height)






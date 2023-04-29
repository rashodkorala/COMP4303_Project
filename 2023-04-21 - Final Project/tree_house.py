
"""
Load and use a world slice.
"""

import random
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


def rotate_point_around_origin(point, angle_degrees):
    angle_radians = np.radians(angle_degrees)
    cos_angle = np.cos(angle_radians)
    sin_angle = np.sin(angle_radians)

    rotated_x = point[0] * cos_angle - point[2] * sin_angle
    rotated_z = point[0] * sin_angle + point[2] * cos_angle

    return np.array([rotated_x, point[1], rotated_z])

def rotate_direction(original_direction, rotation_angle):
    directions = ['north', 'east', 'south', 'west']
    index = directions.index(original_direction)
    new_index = (index + int(rotation_angle / 90)) % len(directions)
    return directions[new_index]

def build_treehouse(editor, starting_pos,tree_height,platform_radius,grid,grid_start):
    block_type = Block("jungle_planks")
    # Generate the tree
    tree_height = 15
    platform_height = tree_height-5
    house_height= platform_radius
    rotation_angle = random.choice([0, 90, 180, 270])
    # Create the platform
    for x in range(-platform_radius, platform_radius + 1):
        for z in range(-platform_radius, platform_radius + 1):
                
                editor.placeBlock(starting_pos + np.array([x, platform_height, z]), Block("jungle_log"))

    # Build walls
    for y in range(house_height):
        for x in range(-platform_radius, platform_radius + 1):
            for z in range(-platform_radius, platform_radius + 1):
                if x in (-platform_radius, platform_radius) or z in (-platform_radius, platform_radius):
                    editor.placeBlock(starting_pos + np.array([x, platform_height + 1 + y, z]), block_type)
                else:
                    editor.placeBlock(starting_pos + np.array([x, platform_height + 1 + y, z]), Block("air"))
    
    #add the tree
    trunk_size = 1
    for y in range(tree_height):
        for x in range(-trunk_size // 2, trunk_size // 2 + 1):
            for z in range(-trunk_size // 2, trunk_size // 2 + 1):
                editor.placeBlock(starting_pos + np.array([x, y, z]), Block("oak_log"))

    # Add windows
    for y in range(1, house_height - 1):
        for x in range(-platform_radius, platform_radius, 2):
            for z in range(-platform_radius, platform_radius, 2):
                if x in (-platform_radius, platform_radius - 1) or z in (-platform_radius, platform_radius - 1) and (x!=platform_radius or z!=-platform_radius):
                    position=starting_pos+rotate_point_around_origin(np.array([x, platform_height + y, z]), rotation_angle)
                    position=position.astype(int)
                    editor.placeBlock(position, Block("glass"))

    # Add a roof
    for x in range(-platform_radius - 1, platform_radius + 2):
        for z in range(-platform_radius - 1, platform_radius + 2):
            editor.placeBlock(starting_pos + np.array([x, platform_height + house_height, z]), Block("jungle_log"))

    # Add a ladder
    for y in range(1, platform_height+3):
        # editor.placeBlock(starting_pos + np.array([0, y, 0]), Block("air"))
        editor.placeBlock(starting_pos + np.array([0, y, -1]), Block("ladder"))
    # Add random spruce leaves around the house and on top
    leaf_density = 0.5  # Adjust this value to control the density of leaves (0.0 to 1.0)

    for y in range(house_height + 2):
        for x in range(-platform_radius - 1, platform_radius + 2):
            for z in range(-platform_radius - 1, platform_radius + 2):
                if ((x in (-platform_radius - 1, platform_radius + 1) or z in (-platform_radius - 1, platform_radius + 1)) or (
                    y == house_height + 1)) and random.random() < leaf_density:
                    editor.placeBlock(starting_pos + np.array([x, platform_height + y, z]), Block("jungle_leaves")) 
    # Add lanterns inside corners
    lantern_positions = [
        (int(platform_radius - 1*0.8), house_height+platform_height-1, int(platform_radius - 1*0.8)),
        (int(-platform_radius + 1*0.8), house_height+platform_height-1, int(platform_radius - 1*0.8)),
        (int(platform_radius - 1*0.8), house_height+platform_height-1, int(-platform_radius + 1*0.8)),
        (int(-platform_radius + 1*0.8), house_height+platform_height-1, int(-platform_radius + 1*0.8))
    ]

    for lantern_position in lantern_positions:
        x, y, z = lantern_position
        editor.placeBlock(starting_pos + np.array([x, y, z]), Block("lantern[hanging=true]"))

    #add a bed 
    bed_positions = [
        (1, platform_height + 1, -platform_radius + 2),
        (2, platform_height + 1, -platform_radius + 2)
    ]
    bed_type=random.choice(["red_bed", "gray_bed", "green_bed", "black_bed","white_bed"])
    for bed_position in bed_positions:
        x, y, z = bed_position
        position=starting_pos+rotate_point_around_origin(np.array([x, y, z]), rotation_angle)
       
        bed_dir=rotate_direction("north", rotation_angle)
        position=position.astype(int)
        editor.placeBlock(position, Block(f'{bed_type}[facing={bed_dir},part=foot]') )

    # Add a cauldron
    cauldron_position = np.array([-platform_radius + 2, platform_height + 1, platform_radius - 1])
    position=starting_pos+rotate_point_around_origin(cauldron_position, rotation_angle)
    position=position.astype(int)
    editor.placeBlock(position, Block("water_cauldron[level=3]"))

    # Add a chest
    chest_position = np.array([-platform_radius + 1, platform_height + 1, -platform_radius + 2])
    position=starting_pos+rotate_point_around_origin(chest_position, rotation_angle)
    position=position.astype(int)
    chest_dir=rotate_direction("east", rotation_angle)
    editor.placeBlock(position, Block(f'chest[facing={chest_dir}]'))

    # Add a barrel
    barrel_position = np.array([platform_radius - 2, platform_height+house_height-1 , platform_radius - 1])
    position=starting_pos+rotate_point_around_origin(barrel_position, rotation_angle)
    position=position.astype(int)
    barr_dir=rotate_direction("north", rotation_angle)
    editor.placeBlock(position, Block(f'barrel[facing={barr_dir}]'))


build_treehouse(editor, buildArea.begin)

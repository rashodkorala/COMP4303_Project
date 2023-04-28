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

height=10

import numpy as np

import math

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


def igloo(editor, center_pos, block_type, radius,grid,grid_local,rotation_angle=0):
    radius=6
    for x in range(-radius, radius + 1):
        for y in range(-1, radius + 1):
            for z in range(-radius, radius + 1):
                local_pos = np.array([x, y, z])
                local_pos = rotate_point_around_origin(local_pos, rotation_angle)
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
                if y== -1 :
                    grid_pos=grid_local+local_pos
                    grid_pos=grid_pos.astype(int)
                    grid.set_grid(grid_pos[0],grid_pos[2],1)
                    editor.placeBlock(position, Block(block_type))
                    if (x<3 and x>-3) and (z<3 and z>-3):
                        editor.placeBlock(position, Block("oak_planks"))
    
    #add carpet to the igloo
    carpet_type = random.choice(["white_carpet", "gray_carpet", "brown_carpet", "black_carpet"])
    for x in range(-radius, radius + 1):
        for z in range(-radius, radius + 1):
            if (x<3 and x>-3) and (z<3 and z>-3) and (x%2==0 or z%2!=0) and (x%2!=0 or z%2==0):
                local_pos = np.array([x, 0, z])
                local_pos = rotate_point_around_origin(local_pos, rotation_angle)
                position = center_pos + local_pos
                position = position.astype(int)
                editor.placeBlock(position, Block(F'{carpet_type}'))


    # for x in range(radius, 1, -1):
    #     position = center_pos + rotate_point_around_origin(np.array([radius-x,0,0]), rotation_angle)
    #     position = position.astype(int)
    #     stair_direction = rotate_direction('east', rotation_angle)
    #     editor.placeBlock(position, Block(f'oak_stairs[facing={stair_direction},half=bottom,shape=straight]'))




    local_pos= np.array([radius-1, 0, 0])
    local_pos = rotate_point_around_origin(local_pos, rotation_angle)
    grid_pos=grid_local+local_pos
    grid_pos=grid_pos.astype(int)
    grid.set_grid(grid_pos[0],grid_pos[2],3) #set the grid to 3 to indicate that there is a door
    position = center_pos + local_pos
    position = position.astype(int)  # Convert the position to integers
    door_direction = rotate_direction('west', rotation_angle)
    editor.placeBlock(position, Block(f'oak_door[facing={door_direction},hinge=left]'))
    editor.placeBlock(position+np.array([1,0,0]), Block('air'))

    local_pos = np.array([-radius +3, 0, 0])
    local_pos = rotate_point_around_origin(local_pos, rotation_angle)
    position = center_pos + local_pos
    position = position.astype(int)  # Convert the position to integers
    bed_direction = rotate_direction('west', rotation_angle)
    bedtype=random.choice(["red_bed","white_bed","black_bed","blue_bed","brown_bed","cyan_bed","gray_bed","green_bed","light_blue_bed","light_gray_bed","lime_bed","magenta_bed","orange_bed","pink_bed","purple_bed","yellow_bed"])
    editor.placeBlock(position, Block(f'{bedtype}[facing={bed_direction},part=foot]'))
    if (radius>5):
        position = position + np.array([0, 0, 1])
        editor.placeBlock(position, Block(f'{bedtype}[facing={bed_direction},part=foot]'))
        position = position + np.array([0, 0, -2])
        editor.placeBlock(position, Block(f'{bedtype}[facing={bed_direction},part=foot]'))

    local_pos = np.array([-radius + 3, 0,radius- 2])
    local_pos = rotate_point_around_origin(local_pos, rotation_angle)
    position = center_pos + local_pos
    position = position.astype(int)  # Convert the position to integers
    editor.placeBlock(position, Block(f'spruce_planks'))
    editor.placeBlock(position+np.array([0,1,0]), Block(f'lantern[hanging=false]'))

    local_pos = np.array([radius -3, 0, -radius + 2])
    local_pos = rotate_point_around_origin(local_pos, rotation_angle)
    position = center_pos + local_pos
    position = position.astype(int)  # Convert the position to integers
    editor.placeBlock(position, Block(f'spruce_planks'))
    editor.placeBlock(position+np.array([0,1,0]), Block(f'lantern[hanging=false]'))

    local_pos = np.array([-radius + 3, 0,-radius+2])
    local_pos = rotate_point_around_origin(local_pos, rotation_angle)
    position = center_pos + local_pos
    position = position.astype(int)  # Convert the position to integers
    editor.placeBlock(position, Block(f'spruce_planks'))
    editor.placeBlock(position+np.array([0,1,0]), Block(f'lantern[hanging=false]'))

    local_pos = np.array([radius-3, 0,radius-2])
    local_pos = rotate_point_around_origin(local_pos, rotation_angle)
    position = center_pos + local_pos
    position = position.astype(int)  # Convert the position to integers
    editor.placeBlock(position, Block(f'spruce_planks'))
    editor.placeBlock(position+np.array([0,1,0]), Block(f'lantern[hanging=false]'))
    

    local_pos = np.array([-radius + 4, 0,-radius+2])
    local_pos = rotate_point_around_origin(local_pos, rotation_angle)
    position = center_pos + local_pos
    position = position.astype(int)  # Convert the position to integers
    chest_direction = rotate_direction('south', rotation_angle)
    editor.placeBlock(position, Block(f'chest[facing={chest_direction}]'))
    

    local_pos = np.array([radius-4, 0,radius-2])
    local_pos = rotate_point_around_origin(local_pos, rotation_angle)
    position = center_pos + local_pos
    position = position.astype(int)  # Convert the position to integers
    trapdoor_direction = rotate_direction('south', rotation_angle)
    editor.placeBlock(position, Block(f'spruce_trapdoor[facing={trapdoor_direction},half=top,open=false]'))
    pot_type="potted_"+random.choice(["dandelion", "poppy", "blue_orchid", "allium", "azure_bluet", "red_tulip", "orange_tulip", "white_tulip", "pink_tulip", "oxeye_daisy", "cornflower", "lily_of_the_valley"])
    editor.placeBlock(position+np.array([0,1,0]), Block(f'minecraft:{pot_type}'))

    #place a cauldron
    local_pos = np.array([radius-5, 0,radius-2])
    local_pos = rotate_point_around_origin(local_pos, rotation_angle)
    position = center_pos + local_pos
    position = position.astype(int)  # Convert the position to integers
    editor.placeBlock(position, Block(f'water_cauldron[level=3]'))
    position = position+np.array([-1,0,0])
    editor.placeBlock(position, Block(f'polished_andesite_slab[type=top]'))

    #place some barrels
    local_pos = np.array([-radius + 5, 1,-radius+2])
    local_pos = rotate_point_around_origin(local_pos, rotation_angle)
    position = center_pos + local_pos
    position = position.astype(int)  # Convert the position to integers
    barrel_dir = rotate_direction('south', rotation_angle)
    editor.placeBlock(position, Block(f'barrel[facing={barrel_dir}]'))
    position = position+np.array([1,0,0])
    editor.placeBlock(position, Block(f'barrel[facing={barrel_dir}]'))
    position = position+np.array([0,-1,0])
    editor.placeBlock(position, Block(f'spruce_trapdoor[facing={barrel_dir},half=top,open=false]'))
    position = position+np.array([-1,0,0])
    editor.placeBlock(position, Block(f'spruce_trapdoor[facing={barrel_dir},half=top,open=false]'))


    #ad campfire at radius ,radius
    local_pos = np.array([radius, 0,radius])
    local_pos = rotate_point_around_origin(local_pos, rotation_angle)
    position = center_pos + local_pos
    position = position.astype(int)  # Convert the position to integers
    campfire_dir = rotate_direction('south', rotation_angle)
    editor.placeBlock(position, Block(f'campfire[facing={campfire_dir},lit=true]'))
# Call the build_igloo() function to create an igloo rotated around the Y-axis by 45 degrees
center_pos = buildArea.begin+np.array([0, 0, 0])
igloo(editor, center_pos, "snow_block", 5, rotation_angle=0)



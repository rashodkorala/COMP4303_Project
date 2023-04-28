
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


def bunker(editor, starting_pos,biome,grid,underground_height=5,grid_local=0):
    #add randome angle out of 90,180,270
    wall_block_type = 'oak_planks'
    roof_block_type = 'spruce_planks'
    floor_block_type = 'oak_planks'
    rotation_angle = 0#random.choice([0,90,180,270])
    length = underground_height + 5 #9
    width = length #9
    
   
    
    roof_height = underground_height + 2 #4
    wall_height = underground_height + 1 #6

    starting_pos=starting_pos+np.array([0,-underground_height,0]) #-5
   
    # Create walls
    for x in range(length):
        for y in range(wall_height, 0, -1):
            for z in range(width):
                position = starting_pos + rotate_point_around_origin(np.array([x, y, z]), rotation_angle)
                position = position.astype(int)
                if x == 0 or x == length - 1 or z == 0 or z == width - 1:    
                    editor.placeBlock(position, Block(wall_block_type))
                else:
                    editor.placeBlock(position, Block('air'))
     # Create floor
    for x in range(length):
        for z in range(width):
            local_pos=grid_local+rotate_point_around_origin(np.array([x,0,z]), rotation_angle)
            local_pos = local_pos.astype(int)
            grid.set_grid(local_pos[0],local_pos[2],1)
            position = starting_pos + rotate_point_around_origin(np.array([x, 0, z]), rotation_angle)
            position = position.astype(int)
            # position = starting_pos + np.array([x, 0, z])
            editor.placeBlock(position, Block(floor_block_type))
    # Create roof
    for y in range(roof_height):
        for x in range(y, length - y):
            for z in range(y, width - y):
                position = starting_pos + rotate_point_around_origin(np.array([x, wall_height + y, z]), rotation_angle)
                position = position.astype(int)
                # position = starting_pos + np.array([x, wall_height + y, z])
                if z == y or z == width - y - 1 or x == y or x == length - y - 1:
                    editor.placeBlock(position, Block(roof_block_type))
                else:
                    editor.placeBlock(position, Block('air'))

    #add stair case from roof to floor (without rotation)
    # for x in range(1, underground_height):
    #     position = starting_pos + rotate_point_around_origin(np.array([x,underground_height-x,width//2]), rotation_angle)
    #     position = position.astype(int)        
    #     # position=starting_pos+np.array([x,underground_height-x,width//2])
    #     editor.placeBlock(position, Block('oak_stairs[facing=west,half=bottom,shape=straight]'))


# Add stair case from roof to floor (with rotation)
    for x in range(1, underground_height):
        position = starting_pos + rotate_point_around_origin(np.array([x, underground_height - x, width // 2]), rotation_angle)
        position = position.astype(int)
        stair_direction = rotate_direction('west', rotation_angle)
        editor.placeBlock(position, Block(f'oak_stairs[facing={stair_direction},half=bottom,shape=straight]'))



    #add a door
    position = starting_pos + rotate_point_around_origin(np.array([0,underground_height,width//2]), rotation_angle)
    position = position.astype(int)
    # position=starting_pos+np.array([0,underground_height,width//2])
    stair_direction = rotate_direction('west', rotation_angle)
    editor.placeBlock(position, Block(f'oak_door[facing={stair_direction},half=lower,hinge=left,open=false,powered=false]'))
    
    position=position+rotate_point_around_origin(np.array([0,2,0]), rotation_angle)
    position = position.astype(int)
    # editor.placeBlock(position+np.array([0,2,0]), Block('spruce_slab[type=bottom]'))
    editor.placeBlock(position, Block('spruce_slab[type=bottom]'))

    #place lanterns in the corners
    for x in range(0, length, length-1):
        for z in range(0, width, width-1):
            position = starting_pos + rotate_point_around_origin(np.array([x, y, z]), rotation_angle)
            position = position.astype(int)
            # position=starting_pos+np.array([x,wall_height,z])
            editor.placeBlock(position, Block('lantern[hanging=false]'))
    
    lantern_positions = [
    np.array([1, wall_height, 1]),
    np.array([1, wall_height, width - 2]),
    np.array([length - 2, wall_height, 1]),
    np.array([length - 2, wall_height, width - 2])
]

    for position in lantern_positions:
        position = starting_pos + rotate_point_around_origin(position, rotation_angle)
        position = position.astype(int)
        editor.placeBlock(position, Block('lantern[hanging=true]'))

    
    #put chest in left
    position=starting_pos+rotate_point_around_origin(np.array([1,1,1]), rotation_angle)
    position = position.astype(int)
    chest_direction = rotate_direction('east', rotation_angle)
    editor.placeBlock(position, Block(f'chest[facing={chest_direction},type=single,waterlogged=false]'))

    #palce barrel in right
    # position=starting_pos+np.array([1,1,width-2])
    position=starting_pos+rotate_point_around_origin(np.array([1,1,width-2]), rotation_angle)
    position = position.astype(int)
    barrel_direction = rotate_direction('east', rotation_angle)
    editor.placeBlock(position, Block(f'barrel[facing={barrel_direction},open=true]'))
    position=position+rotate_point_around_origin(np.array([0,0,-1]), rotation_angle)
    position = position.astype(int)
    editor.placeBlock(position, Block('water_cauldron[level=3]'))

    #place a pottte plant
    # position=starting_pos+np.array([1,2,width-2])
    position=starting_pos+rotate_point_around_origin(np.array([1,2,width-2]), rotation_angle)
    position = position.astype(int)
    editor.placeBlock(position, Block('potted_cactus'))

    #place a bed
    for z in range(2, width-2):
        # position=starting_pos+np.array([length-3,1,z])
        position=starting_pos+rotate_point_around_origin(np.array([length-3,1,z]), rotation_angle)
        position = position.astype(int)
        bed_direction = rotate_direction('east', rotation_angle)
        editor.placeBlock(position, Block(f'red_bed[facing={bed_direction},part=foot]'))

    return length

    

    


# Set the starting position and block types
starting_pos = buildArea.begin+np.array([25,0,25])


# Call the function to create the wooden barrack in Minecraft
rotation_angle = 90

# bunker(editor, starting_pos, wall_block_type, roof_block_type, floor_block_type, rotation_angle)

#!/usr/bin/env python3

"""
Load and use a world slice.
"""

import sys
import random

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

def add(vec1, vec2):
    return tuple(a + b for a, b in zip(vec1, vec2))

desert_roof_blocks = ["minecraft:nether_bricks", "minecraft:deepslate_bricks"]
plains_jungles_roof_blocks = ["minecraft:stone_bricks", "minecraft:dark_oak_planks"]
snow_roof_blocks = ["minecraft:blue_ice", "minecraft:black_stained_glass"]

desert_wall_blocks = ["minecraft:mud_bricks", "minecraft:infested_chiseled_stone_bricks"] 
plains_jungles_wall_blocks = ["minecraft:sandstone", "minecraft:chiseled_red_sandstone"]
snow_wall_blocks = ["minecraft:bricks", "minecraft:stripped_oak_log"]

block_selection = random.randint(0,1)

def blocks_for_this_biome(part, biome = None):
    
    if biome == "minecraft:desert":
        if part == "roof":
            block = Block(desert_roof_blocks[block_selection])
        if part == "walls":
            block = Block(desert_wall_blocks[block_selection])

    elif biome == "minecraft:plains" or biome == "minecraft:jungle":
        if part == "roof":
            block = Block(plains_jungles_roof_blocks[block_selection])
        if part == "walls":
            block = Block(plains_jungles_wall_blocks[block_selection])

    elif biome == "minecraft:snowy_tundra":
        if part == "roof":
            block = Block(snow_roof_blocks[block_selection])
        if part == "walls":
            block = Block(snow_wall_blocks[block_selection])

    #need to improve else condition
    else:
       block = Block(floor_blocks[block_selection])

    return block




def make_roof(editor, size, block_type, pyramid_starting_pos):
    for y in range(size):
        for x in range(-size + y + 1, size - y):
            for z in range(-size + y + 1, size - y):
                position = pyramid_starting_pos + np.array([x, y, z])
                if (abs(x) == size - y - 1 or abs(z) == size - y - 1 ):
                    editor.placeBlock(position, Block(block_type))
                else:
                    editor.placeBlock(position, Block("minecraft:air"))



def build_tiny_house(center, editor, base_level=0, biome=None):
    """
    Build a tiny house at the specified center position.
    """
    house_height = random.randint(6,8)
    house_width = house_height
    #height= 5
    starting_pos= add(center, (0, house_height-1, 0))

    #clear the area
    
    
    #build the floor
    for x in range(-house_width // 2, house_width // 2 + 1):
        for z in range(-house_width // 2, house_width // 2 + 1):

            #replaces the default floor with preferred block    

            editor.placeBlock(add(center, (x, base_level-1, z)), blocks_for_this_biome("walls", "minecraft:snowy_tundra"))

    # Build the walls
    for x in range(-house_width // 2, house_width // 2 + 1):
        for y in range(base_level, base_level + house_height):
            for z in range(-house_width // 2, house_width // 2 + 1):
                if x == -house_width // 2 or x == house_width // 2 or z == -house_width // 2 or z == house_width // 2:
                    editor.placeBlock(add(center, (x, y, z)), blocks_for_this_biome("walls", "minecraft:snowy_tundra"))
                else:
                    editor.placeBlock(add(center, (x, y, z)), Block("minecraft:air"))
                    
    # Build the roof
    if house_height%2==0:
        make_roof(editor, house_width//2+1, blocks_for_this_biome("roof", "minecraft:snowy_tundra"), starting_pos)
    else:
        make_roof(editor, house_width//2+2, blocks_for_this_biome("roof", "minecraft:snowy_tundra"), starting_pos)

    # Build the door
    # editor.placeBlock(add(center, (0, base_level, -house_width // 2)), Block("iron door"))
    editor.placeBlock(add(center, (0, base_level, -house_width // 2)), Block("spruce_door"))
    editor.placeBlock(add(center, (-1, base_level +2, -house_width // 2-1)), Block("minecraft:wall_torch[facing=north]"))
    editor.placeBlock(add(center, (1, base_level +2, -house_width // 2-1)), Block("minecraft:wall_torch[facing=north]"))

    # Build windows
    for z in range(-house_width // 2, house_width // 2):
        rand= random.randint(2,house_width-2)
        editor.placeBlock(add(center, (-house_width // 2, base_level +rand, z)), Block("minecraft:glass_pane"))
        # editor.placeBlock(add(center, (house_width // 2, base_level + 1, -z)), Block("minecraft:glass_pane"))
        editor.placeBlock(add(center, (house_width // 2, base_level + 1,-z)), Block("minecraft:glass_pane"))
        editor.placeBlock(add(center, (z, base_level + random.randint(3,house_width-2), -house_width // 2)), Block("minecraft:glass_pane"))
        editor.placeBlock(add(center, (z, base_level + random.randint(3,house_width-2), house_width // 2)), Block("minecraft:glass_pane"))

    editor.placeBlock(add(center, (house_width // 2, base_level + 1, 0)), Block("minecraft:glass_pane"))
    editor.placeBlock(add(center, (0, base_level + 1, house_width // 2)), Block("minecraft:glass_pane"))

    # Place the bed
    editor.placeBlock(add(center, (-house_width//2+2, base_level, house_width//2-2)), Block("minecraft:red_bed[part=foot, facing=south]"))
    if (house_width > 6):
        editor.placeBlock(add(center, (-house_width//2+3, base_level, house_width//2-2)), Block("minecraft:red_bed[part=foot, facing=south]"))
    #place table next bed
    editor.placeBlock(add(center, (-house_width//2+1, base_level,house_width // 2-1)), Block("minecraft:spruce_planks"))
    editor.placeBlock(add(center, (-house_width//2+1, base_level, house_width // 2-2)), Block("minecraft:spruce_trapdoor[facing=north, half=bottom, open=true]"))


    #place lantern
    editor.placeBlock(add(center, (-house_width//2+1, base_level + 1, house_width // 2-1)), Block("minecraft:lantern[hanging=false]"))

    #place barrel
    editor.placeBlock(add(center, (house_width//2-1, base_level+2,  house_width // 2-1)), Block("minecraft:barrel[facing=north]"))
    editor.placeBlock(add(center, (house_width//2-2, base_level+2,  house_width // 2-1)), Block("minecraft:barrel[facing=north]"))

    editor.placeBlock(add(center, (house_width//2-1, base_level+1,  house_width // 2-1)), Block("minecraft:spruce_trapdoor[facing=north, half=top, open=false]"))
    editor.placeBlock(add(center, (house_width//2-2, base_level+1,  house_width // 2-1)), Block("minecraft:spruce_trapdoor[facing=north, half=top, open=false]"))
    
    #place cauldron
    editor.placeBlock(add(center, (house_width//2-1, base_level,  house_width // 2-1)), Block("minecraft:water_cauldron[level=3]"))
    #place flower pot
    editor.placeBlock(add(center, (-house_width//2+1, base_level+1,-house_width // 2+1)), Block("minecraft:spruce_trapdoor[facing=east, half=top, open=false]"))
    editor.placeBlock(add(center, (-house_width//2+1, base_level+2,-house_width // 2+1)), Block("minecraft:potted_oak_sapling"))

    #place chest
    editor.placeBlock(add(center, (-house_width//2+1, base_level+3, -house_width//2+3)), Block("minecraft:chest[facing=east]"))
    editor.placeBlock(add(center, (-house_width//2+1, base_level+3, -house_width//2+2)), Block("minecraft:chest[facing=east]"))
    editor.placeBlock(add(center, (-house_width//2+1, base_level+2, -house_width//2+3)), Block("minecraft:spruce_trapdoor[facing=east, half=top, open=false]"))
    editor.placeBlock(add(center, (-house_width//2+1, base_level+2, -house_width//2+2)), Block("minecraft:spruce_trapdoor[facing=east, half=top, open=false]"))

    #add lanterns to corners of the house if it is big enough
    if (house_width > 7):
        editor.placeBlock(add(center, (-house_width//2+2, house_width, -house_width//2+3)), Block("minecraft:lantern[hanging=true]"))
        editor.placeBlock(add(center, (-house_width//2+2, house_width, house_width//2-3)), Block("minecraft:lantern[hanging=true]"))
        editor.placeBlock(add(center, (house_width//2-2, house_width, -house_width//2+3)), Block("minecraft:lantern[hanging=true]"))
        editor.placeBlock(add(center, (house_width//2-2, house_width, house_width//2-3)), Block("minecraft:lantern[hanging=true]"))
    return house_width, house_height

print(buildArea.size.x, buildArea.size.z)
print(buildArea.begin.x, buildArea.begin.z)



for i in range(3):
    x = random.randint(0, buildArea.size.x)
    z = random.randint(0,  buildArea.size.z)
    build_tiny_house(buildArea.begin + [x, 0, z], editor)
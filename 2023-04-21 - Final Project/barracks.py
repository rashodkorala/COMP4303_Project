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

# def add(vec1, vec2):
#     return tuple(a + b for a, b in zip(vec1, vec2))

desert_roof_blocks = ["minecraft:nether_bricks", "minecraft:deepslate_bricks"]
plains_jungles_roof_blocks = ["minecraft:stone_bricks", "minecraft:dark_oak_planks"]
snow_roof_blocks = ["minecraft:blue_ice", "minecraft:black_stained_glass"]

desert_wall_blocks = ["minecraft:mud_bricks", "minecraft:infested_chiseled_stone_bricks"] 
plains_jungles_wall_blocks = ["minecraft:sandstone", "minecraft:chiseled_red_sandstone"]
snow_wall_blocks = ["minecraft:bricks", "minecraft:stripped_oak_log"]
floor_blocks= ["minecraft:polished_andesite", "minecraft:polished_diorite", "minecraft:polished_granite"]
block_selection = random.randint(0,1)

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

def blocks_for_this_biome(part, biome):
    block = None
    if "desert" in biome:
        if "roof" in part:
            block = Block(desert_roof_blocks[block_selection])
        if "walls" in part:
            block = Block(desert_wall_blocks[block_selection])

    elif "plains" in biome or "jungle" in biome:
        if "roof" in part:
            block = Block(plains_jungles_roof_blocks[block_selection])
        if "walls" in part:
            block = Block(plains_jungles_wall_blocks[block_selection])

    elif "snow" in biome or "snowy" in biome:
        if "roof" in part:
            block = Block(snow_roof_blocks[block_selection])
        if "walls" in part:
            block = Block(snow_wall_blocks[block_selection])

    #need to improve else condition
    elif biome is None:
       block = Block(floor_blocks[block_selection])

    return block

def make_roof(editor, size, block_type, starting_pos, rotation_angle):
 
    for y in range(size):
        for x in range(-size + y + 1, size - y):
            for z in range(-size + y + 1, size - y):
                position=starting_pos+rotate_point_around_origin(np.array([x, y, z]), rotation_angle)
                # position = pyramid_starting_pos + np.array([x, y, z])
                position = position.astype(int)
                if abs(x) == size - y - 1 or abs(z) == size - y - 1 : 
                    editor.placeBlock(position, Block(block_type))
                else:
                    editor.placeBlock(position, Block('air'))

    for x in range(length):
        for y in range(wall_height, 0, -1):
            for z in range(width):
                position = starting_pos + rotate_point_around_origin(np.array([x, y, z]), rotation_angle)
                position = position.astype(int)
                if not (x == 0 or x == length - 1 or z == 0 or z == width - 1): 
                    editor.placeBlock(position, Block('air'))
     # Create floor
    for x in range(length):
        for z in range(width):
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

#                 if abs(x) == size-y-1 or abs(z)==size-y-1:
#                     editor.placeBlock(position, Block(block_type))
#                 else:
#                     editor.placeBlock(position, Block("minecraft:air"))





def barracks(editor, center, base_level=0,biome=None,rotation_angle=180):
    """
    Build a tiny house at the specified center position.
    """
    #choose randome even number between 6 and 8
    house_height = 8 #random.randint(6,8)
    house_width = house_height
    biome = "plains"
    # roof_starting_pos=center+rotate_point_around_origin(np.array([0, house_height-1, 0]), rotation_angle)
    # roof_starting_pos=roof_starting_pos.astype(int)

    wall_block=blocks_for_this_biome("walls", biome)
    roof_block=blocks_for_this_biome("roof", biome)
    floor_block=blocks_for_this_biome("floor", biome)
    
    #build the floor
    for x in range(-house_width // 2, house_width // 2 + 1):
        for z in range(-house_width // 2, house_width // 2 + 1):
            #replaces the default floor with preferred block    
            position=center + rotate_point_around_origin(np.array([x, base_level-1, z]), rotation_angle)
            position=position.astype(int)
            editor.placeBlock(position, Block("spruce_planks"))
            #add the x,z coordinates to the grid
            

    # Build the walls
    for x in range(-house_width // 2, house_width // 2 + 1):
        for y in range(base_level, base_level + house_height):
            for z in range(-house_width // 2, house_width // 2 + 1):
                position=center+rotate_point_around_origin(np.array([x, y, z]), rotation_angle)
                position=position.astype(int)
                if x == -house_width // 2 or x == house_width // 2 or z == -house_width // 2 or z == house_width // 2:
                    editor.placeBlock(position, wall_block)
                else:
                    editor.placeBlock(position, Block("minecraft:air"))
                    
    # Build the roof
    if house_height%2==0:
        make_roof(editor, house_width//2+1,roof_block, center+np.array([0,house_height-1,0]),rotation_angle)
    else:
        make_roof(editor,1,roof_block , center+np.array([0,house_height-1,0]),rotation_angle)

    # Build the door
    position=center+rotate_point_around_origin(np.array([0, base_level, -house_width // 2]), rotation_angle)
    position=position.astype(int)
    door_dir=rotate_direction("south", rotation_angle)
    editor.placeBlock(position, Block(f'spruce_door[facing={door_dir}]'))
    
    position=center+rotate_point_around_origin(np.array([-1, base_level+2, -house_width // 2-1]), rotation_angle)
    position=position.astype(int)
    wall_torch_dir=rotate_direction("north", rotation_angle)
    editor.placeBlock(position, Block(f'wall_torch[facing={wall_torch_dir}]'))

    position=center+rotate_point_around_origin(np.array([1, base_level+2, -house_width // 2-1]), rotation_angle)
    position=position.astype(int)
    editor.placeBlock(position, Block(f'wall_torch[facing={wall_torch_dir}]'))

    # Build windows
    for z in range(-house_width // 2, house_width // 2):
        rand= random.randint(2,house_width-2)
        position=center+rotate_point_around_origin(np.array([-house_width // 2, base_level +rand, z]), rotation_angle)
        position=position.astype(int)
        editor.placeBlock(position, Block("minecraft:glass_pane"))
        # editor.placeBlock(add(center, (-house_width // 2, base_level +rand, z)), Block("minecraft:glass_pane"))
        position=center+rotate_point_around_origin(np.array([house_width // 2, base_level +1, -z]), rotation_angle)
        position=position.astype(int)
        editor.placeBlock(position, Block("minecraft:glass_pane"))
        # editor.placeBlock(add(center, (house_width // 2, base_level + 1,-z)), Block("minecraft:glass_pane"))
        
        position=center+rotate_point_around_origin(np.array([z, base_level + random.randint(3,house_width-2), -house_width // 2]), rotation_angle)
        position=position.astype(int)
        editor.placeBlock(position, Block("minecraft:glass_pane"))
        # editor.placeBlock(add(center, (z, base_level + random.randint(3,house_width-2), -house_width // 2)), Block("minecraft:glass_pane"))
        
        position=center+rotate_point_around_origin(np.array([z, base_level + random.randint(3,house_width-2), house_width // 2]), rotation_angle)
        position=position.astype(int)
        editor.placeBlock(position, Block("minecraft:glass_pane"))
        # editor.placeBlock(add(center, (z, base_level + random.randint(3,house_width-2), house_width // 2)), Block("minecraft:glass_pane"))

    position=center+rotate_point_around_origin(np.array([-house_width // 2, base_level +1, 0]), rotation_angle)
    position=position.astype(int)
    editor.placeBlock(position, Block("minecraft:glass_pane"))
    position=center+rotate_point_around_origin(np.array([0, base_level +1, house_width // 2]), rotation_angle)
    position=position.astype(int)
    editor.placeBlock(position, Block("minecraft:glass_pane"))

    # editor.placeBlock(add(center, (house_width // 2, base_level + 1, 0)), Block("minecraft:glass_pane"))
    # editor.placeBlock(add(center, (0, base_level + 1, house_width // 2)), Block("minecraft:glass_pane"))

    # Place the bed
    position=center+rotate_point_around_origin(np.array([-house_width // 2+2, base_level, house_width // 2-2]), rotation_angle)
    position=position.astype(int)
    bedtype=random.choice(["red_bed","white_bed","black_bed","blue_bed","brown_bed","cyan_bed","gray_bed","green_bed","light_blue_bed","light_gray_bed","lime_bed","magenta_bed","orange_bed","pink_bed","purple_bed","yellow_bed"])
    bed_dir=rotate_direction("south", rotation_angle)
    editor.placeBlock(position, Block(f'{bedtype}[facing={bed_dir}]'))
    # editor.placeBlock(add(center, (-house_width//2+2, base_level, house_width//2-2)), Block("minecraft:red_bed[part=foot, facing=south]"))
    if (house_width > 6):
        position=center+rotate_point_around_origin(np.array([-house_width // 2+3, base_level, house_width // 2-2]), rotation_angle)
        position=position.astype(int)
        editor.placeBlock(position, Block(f'{bedtype}[facing={bed_dir}]'))
        # editor.placeBlock(add(center, (-house_width//2+3, base_level, house_width//2-2)), Block("minecraft:red_bed[part=foot, facing=south]"))
    #place table next bed

    position=center+rotate_point_around_origin(np.array([-house_width // 2+1, base_level, house_width // 2-1]), rotation_angle)
    position=position.astype(int)
    editor.placeBlock(position, Block("minecraft:spruce_planks"))
    position=center+rotate_point_around_origin(np.array([-house_width // 2+1, base_level, house_width // 2-2]), rotation_angle)
    position=position.astype(int)
    trapdoor_dir=rotate_direction("north", rotation_angle)
    editor.placeBlock(position, Block(f'minecraft:spruce_trapdoor[facing={trapdoor_dir}, half=bottom, open=true]'))
    # editor.placeBlock(add(center, (-house_width//2+1, base_level,house_width // 2-1)), Block("minecraft:spruce_planks"))
    # editor.placeBlock(add(center, (-house_width//2+1, base_level, house_width // 2-2)), Block("minecraft:spruce_trapdoor[facing=north, half=bottom, open=true]"))


    #place lantern
    position=center+rotate_point_around_origin(np.array([-house_width // 2+1, base_level + 1, house_width // 2-1]), rotation_angle)
    position=position.astype(int)
    editor.placeBlock(position, Block("minecraft:lantern[hanging=false]"))

    # editor.placeBlock(add(center, (-house_width//2+1, base_level + 1, house_width // 2-1)), Block("minecraft:lantern[hanging=false]"))

    #place barrel
    position=center+rotate_point_around_origin(np.array([house_width // 2-1, base_level + 2, house_width // 2-1]), rotation_angle)
    position=position.astype(int)
    barrel_dir=rotate_direction("north", rotation_angle)
    editor.placeBlock(position, Block(f'minecraft:barrel[facing={barrel_dir}]'))
    editor.placeBlock(position+np.array([0,-1,0]), Block(f'minecraft:spruce_trapdoor[facing={barrel_dir}, half=top, open=false]'))
    # editor.placeBlock(add(center, (house_width//2-1, base_level+2,  house_width // 2-1)), Block("minecraft:barrel[facing=north]"))
    position=center+rotate_point_around_origin(np.array([house_width // 2-2, base_level + 2, house_width // 2-1]), rotation_angle)
    position=position.astype(int)
    editor.placeBlock(position, Block(f'minecraft:barrel[facing={barrel_dir}]'))
    editor.placeBlock(position+np.array([0,-1,0]), Block(f'minecraft:spruce_trapdoor[facing={barrel_dir}, half=top, open=false]'))
    # editor.placeBlock(add(center, (house_width//2-2, base_level+2,  house_width // 2-1)), Block("minecraft:barrel[facing=north]"))


    #place trapdoor under barrel
    
    # editor.placeBlock(position, Block("minecraft:spruce_trapdoor[facing=north, half=top, open=false]"))
    # editor.placeBlock(add(center, (house_width//2-2, base_level+1,  house_width // 2-1)), Block("minecraft:spruce_trapdoor[facing=north, half=top, open=false]"))
    
    #place cauldron
    position=center+rotate_point_around_origin(np.array([house_width // 2-1, base_level, house_width // 2-1]), rotation_angle)
    position=position.astype(int)
    editor.placeBlock(position, Block("minecraft:water_cauldron[level=3]"))
    # editor.placeBlock(add(center, (house_width//2-1, base_level,  house_width // 2-1)), Block("minecraft:water_cauldron[level=3]"))
    #place flower pot
    position=center+rotate_point_around_origin(np.array([-house_width // 2+1, base_level+1,-house_width // 2+1]), rotation_angle)
    position=position.astype(int)
    trapdoor_dir=rotate_direction("east", rotation_angle)
    editor.placeBlock(position, Block(f'minecraft:spruce_trapdoor[facing={trapdoor_dir}, half=top, open=false]'))
    position=position+np.array([0,+1,0])
    pot_type="potted_"+random.choice(["dandelion", "poppy", "blue_orchid", "allium", "azure_bluet", "red_tulip", "orange_tulip", "white_tulip", "pink_tulip", "oxeye_daisy", "cornflower", "lily_of_the_valley"])
    editor.placeBlock(position, Block(f'minecraft:{pot_type}'))
    # editor.placeBlock(add(center, (-house_width//2+1, base_level+1,-house_width // 2+1)), Block("minecraft:spruce_trapdoor[facing=east, half=top, open=false]"))
    # editor.placeBlock(add(center, (-house_width//2+1, base_level+2,-house_width // 2+1)), Block("minecraft:potted_oak_sapling"))

    #place chest
    position=center+rotate_point_around_origin(np.array([-house_width // 2+1, base_level+3,-house_width // 2+3]), rotation_angle)
    position=position.astype(int)
    chest_dir=rotate_direction("east", rotation_angle)
    editor.placeBlock(position, Block(f'minecraft:chest[facing={chest_dir}]'))
    position=position+np.array([0,0,1])
    editor.placeBlock(position, Block(f'minecraft:chest[facing={chest_dir}]'))
    position=position+np.array([0,-1,0])
    editor.placeBlock(position, Block(f'minecraft:spruce_trapdoor[facing={chest_dir}, half=top, open=false]'))
    position=position+np.array([0,0,-1])
    editor.placeBlock(position, Block(f'minecraft:spruce_trapdoor[facing={chest_dir}, half=top, open=false]'))
    # editor.placeBlock(add(center, (-house_width//2+1, base_level+3, -house_width//2+3)), Block("minecraft:chest[facing=east]"))
    # editor.placeBlock(add(center, (-house_width//2+1, base_level+3, -house_width//2+2)), Block("minecraft:chest[facing=east]"))
    # editor.placeBlock(add(center, (-house_width//2+1, base_level+2, -house_width//2+3)), Block("minecraft:spruce_trapdoor[facing=east, half=top, open=false]"))
    # editor.placeBlock(add(center, (-house_width//2+1, base_level+2, -house_width//2+2)), Block("minecraft:spruce_trapdoor[facing=east, half=top, open=false]"))

    #add lanterns to corners of the house if it is big enough
    if (house_width > 7):
        position=center+rotate_point_around_origin(np.array([-house_width // 2+2, house_width, -house_width // 2+3]), rotation_angle)
        position=position.astype(int)
        editor.placeBlock(position, Block("minecraft:lantern[hanging=true]"))

        position=center+rotate_point_around_origin(np.array([-house_width // 2+2, house_width, house_width // 2-3]), rotation_angle)
        position=position.astype(int)
        editor.placeBlock(position, Block("minecraft:lantern[hanging=true]"))

        position=center+rotate_point_around_origin(np.array([house_width // 2-2, house_width, -house_width // 2+3]), rotation_angle)
        position=position.astype(int)
        editor.placeBlock(position, Block("minecraft:lantern[hanging=true]"))

        position=center+rotate_point_around_origin(np.array([house_width // 2-2, house_width, house_width // 2-3]), rotation_angle)
        position=position.astype(int)
        editor.placeBlock(position, Block("minecraft:lantern[hanging=true]"))
        # editor.placeBlock(add(center, (-house_width//2+2, house_width, -house_width//2+3)), Block("minecraft:lantern[hanging=true]"))
        # editor.placeBlock(add(center, (-house_width//2+2, house_width, house_width//2-3)), Block("minecraft:lantern[hanging=true]"))
        # editor.placeBlock(add(center, (house_width//2-2, house_width, -house_width//2+3)), Block("minecraft:lantern[hanging=true]"))
        # editor.placeBlock(add(center, (house_width//2-2, house_width, house_width//2-3)), Block("minecraft:lantern[hanging=true]"))

""" biome=editor.getBiome(buildArea.begin)
print(biome)
barracks(buildArea.begin, editor,biome=biome)



for i in range(3):
    x = random.randint(0, buildArea.size.x)
    z = random.randint(0,  buildArea.size.z)
    barracks(buildArea.begin + [x, 0, z], editor) """

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


""" def make_archerTower(editor, starting_pos, wall_block_type, roof_block_type, floor_block_type, window_block_type, staircase_block_type):
    # Define dimensions and parameters
    length = 7
    width = 7
    wall_height = 7
    roof_height = 7
    line_height = 1
    size_reduction = 1
    
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
                            editor.placeBlock(position+np.array([0,0,width-1]), Block(window_block_type))

    # Create roof
    roof_starting_pos = starting_pos + np.array([length // 2 - 1, 2 * wall_height   , width // 2 - 1])
    # Set the height of the pyramid
    height = 5
    # roof_starting_pos =buildArea.begin+np.array([0,0,0])
    block_type = 'stone_bricks'

# Call the function to create the pyramid and its reflection in Minecraft
    create_pyramid_and_reflection_in_xz_plane(editor, roof_starting_pos, block_type, height)
    # make_roof(editor, length+3, width+3, roof_height, roof_starting_pos, roof_block_type, line_height, size_reduction) """

""" def create_archer_tower(editor, starting_pos, wall_block_type, floor_block_type, ladder_block_type):
    base_length = 12
    base_width = 12
    tower_length = 6
    tower_width = 6
    wall_height = 10
    battlement_height = 2
    num_floors = 2  

    # Create base
    for x in range(base_length):
        for z in range(base_width):
            position = starting_pos + np.array([x, 0, z])
            editor.placeBlock(position, Block(wall_block_type))

    # Create tower walls and ladder
    for floor in range(num_floors):
        for x in range(tower_length):
            for y in range(wall_height):
                for z in range(tower_width):
                    if x == 0 or x == tower_length - 1 or z == 0 or z == tower_width - 1:
                        position = starting_pos + np.array([x + 2, 1 + floor * (wall_height)-1 + y, z + 2])
                        editor.placeBlock(position, Block(wall_block_type))
                    else:
                        position = starting_pos + np.array([x + 2, 1 + floor * (wall_height + 1)-1 + y, z + 2])
                        editor.placeBlock(position, Block("air"))
                        
        # Create tower floors
        for x in range(tower_length):
            for z in range(tower_width):
                position = starting_pos + np.array([x + 2, 1 + floor * (wall_height), z + 2])
                editor.placeBlock(position, Block(floor_block_type))

        
        for y in range(wall_height):
            position = starting_pos + np.array([tower_length - 2, 1 + floor * (wall_height+1) + y, tower_width])
            # editor.placeBlock(position+np.array([0,0,1]), Block(wall_block_type))
            editor.placeBlock(position, Block("air"))
            editor.placeBlock(position, Block(ladder_block_type + "[facing=north]"))

    # Create battlements
    for x in range(tower_length):
        for y in range(battlement_height):
            for z in range(tower_width):
                if (x == 0 or x == tower_length - 1 or z == 0 or z == tower_width - 1) and (y == 0 or (x + y) % 2 == 0):
                    position = starting_pos + np.array([x + 2,num_floors * (wall_height) + y, z + 2])
                    editor.placeBlock(position, Block(wall_block_type))
    
    # Create battlement floor
    for x in range(tower_length):
        for z in range(tower_width):
            position = starting_pos + np.array([x + 2,num_floors * (wall_height-2), z + 2])
            editor.placeBlock(position, Block(floor_block_type))
    
# Set the starting position and block types
starting_pos = buildArea.begin+np.array([0, 0, 0])
wall_block_type = 'stone_bricks'
floor_block_type = 'stone_bricks'
ladder_block_type = 'ladder'

# Call the function to create the archer tower in Minecraft
create_archer_tower(editor, starting_pos, wall_block_type, floor_block_type, ladder_block_type) """

""" def make_roof(editor, length, width, height, starting_pos, block_type, line_height, size_reduction):
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
                        editor.placeBlock(position, Block("minecraft:air")) """

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

def build_floor(editor, starting_pos, block_type, floor_width,local_pos, floor_height,grid):
    for i in range(-floor_width, floor_width + 1):
        for j in range(-floor_width, floor_width + 1):
            grid_pos=local_pos+np.array([i,0,j])
            grid.set_grid(grid_pos[0],grid_pos[2],1)
            position = starting_pos + np.array([i, floor_height, j])
            editor.placeBlock(position, Block(block_type))

def build_stage_floor(editor, starting_pos, block_type, floor_width,local_pos, floor_height,grid):
    min=heightmap.min()
    for y in range(min,0,-1):
        for i in range(-floor_width, floor_width + 1):
            for j in range(-floor_width, floor_width + 1):
                is_corner = abs(i) == floor_width  and abs(j) == floor_width 
            
            if is_corner:
                position = starting_pos + np.array([i, floor_height-y, j])
                editor.placeBlock(position, Block(block_type))

def build_ladders(editor, starting_pos, ladder_type, size, building_h, rotation_angle):
    for y in range(1,building_h):
        position = starting_pos +rotate_point_around_origin(np.array([-size+2, y, 0]),rotation_angle)
        position=position.astype(int)
        editor.placeBlock(position, Block("air"))
        editor.placeBlock(position, Block(ladder_type))

def add_torches(editor, starting_pos, torch_type,base_block, size, building_h, interval):

    for y in range(0, building_h, interval):
        for i in range(size):
            # Add torches to the left wall
            position_left = starting_pos + np.array([-size + i + 1, y, i])
            editor.placeBlock(position_left, Block(base_block))
            position_left = position_left + np.array([0,1,0])
            editor.placeBlock(position_left, Block(torch_type))

            # Add torches to the right wall
            position_right = starting_pos + np.array([size - i - 1, y, i])
            editor.placeBlock(position_right, Block(base_block))
            position_right = position_right + np.array([0,1,0])
            editor.placeBlock(position_right, Block(torch_type))

            # Add torches to the reflected left wall
            position_ref_left = starting_pos + np.array([-size + i + 1, y, -i])
            editor.placeBlock(position_ref_left, Block(base_block))
            position_ref_left = position_ref_left + np.array([0,1,0])
            editor.placeBlock(position_ref_left, Block(torch_type))

            # Add torches to the reflected right wall
            position_ref_right = starting_pos + np.array([size - i - 1, y, -i])
            editor.placeBlock(position_ref_right, Block(base_block))
            position_ref_right = position_ref_right + np.array([0,1,0])
            editor.placeBlock(position_ref_right, Block(torch_type))

# In the archerTowerpy() function, call add_torches() after build_ladders()

def add_windows(editor, starting_pos, window_type, height, building_h, interval, window_size):
    for y in range(1, building_h, interval):
        for i in range(height):
            for w in range(1, window_size + 1):
                # Add windows to the left wall
                position_left = starting_pos + np.array([-height + i + 1, y + w, i])
                editor.placeBlock(position_left, Block(window_type))

                # Add windows to the right wall
                position_right = starting_pos + np.array([height - i - 1, y + w, i])
                editor.placeBlock(position_right, Block(window_type))

                # Add windows to the reflected left wall
                position_ref_left = starting_pos + np.array([-height + i + 1, y + w, -i])
                editor.placeBlock(position_ref_left, Block(window_type))

                # Add windows to the reflected right wall
                position_ref_right = starting_pos + np.array([height - i - 1, y + w, -i])
                editor.placeBlock(position_ref_right, Block(window_type))

# In the archerTowerpy() function, call add_windows() after add_torches()

def get_archer_tower_dimensions():
    building_height = 20
    size = random.choice([4, 6])
    
    return (building_height, size)


def archer_tower(editor, starting_pos,biome,size,grid,local_pos):
    block_type = 'stone_bricks'
    rotation_angle=random.choice([0,90,180,270])
    building_h = get_archer_tower_dimensions()[0]
    size = get_archer_tower_dimensions()[1]

    floor_height = building_h

    build_stage_floor(editor, starting_pos, block_type, size, local_pos,floor_height=0,grid=grid)
    # Build the pyramid
    if biome == "plains" or biome == "forest":
        roof_block_type = random.choice([])
    if biome == "snow_biome":
        roof_block_type = random.choice(["blue_ice", "quartz_block", "bricks"])
    if biome == "desert":
        roof_block_type = random.choice(["sandstone", "red_sandstone", "crying_obsidian"])
        
    for y in range(floor_height):
        for i in range(size):
            for j in range(-size + i + 1  , size - i):
                if j == -size + i + 1 or j == size - i - 1:
                    position = starting_pos + np.array([j, y, i])
                    # editor.placeBlock(position, Block(block_type))
                    editor.placeBlock(position, Block(random.choice(["mossy_stone_bricks", "stone_bricks", "cracked_stone_bricks"])))
                # elif (y==0 or y==floor_height//2):
                #     position = starting_pos + np.array([j, y, i])
                #     editor.placeBlock(position, Block(block_type))
                else:
                    position = starting_pos + np.array([j, y, i])
                    editor.placeBlock(position, Block("air")) 
        
    # Build the reflection of the pyramid
        for i in range(size):
            for j in range(-size + i + 1, size - i):
                if j == -size + i + 1 or j == size - i - 1:
                    position = starting_pos + np.array([j, y, -i])
                    # editor.placeBlock(position, Block(block_type)) 
                    editor.placeBlock(position, Block(random.choice(["mossy_stone_bricks", "stone_bricks", "cracked_stone_bricks"])))
                else:
                    position = starting_pos + np.array([j, y, i])
                    editor.placeBlock(position, Block("air"))
    
    #add a door to the tower
    
    # Build the floor
    build_floor(editor, starting_pos, block_type, size, local_pos,floor_height=0,grid=grid)
    build_floor(editor, starting_pos, block_type, size-1, local_pos,floor_height-4,grid=grid)
    

    add_torches(editor, starting_pos, "lantern[hanging=false]","spruce_slab[type=top]",size-1, building_h, interval=4)
    add_windows(editor, starting_pos, "tinted_glass", size, building_h-1, interval=6, window_size=1)
    ladder_dir=rotate_direction("east", rotation_angle)
    build_ladders(editor, starting_pos, f'ladder[facing={ladder_dir}]', size, building_h,rotation_angle=rotation_angle)

    position = starting_pos +rotate_point_around_origin(np.array([size-1, 1, 0]), rotation_angle)
    position=position.astype(int)
    editor.placeBlock(position, Block("air"))

    position = starting_pos +rotate_point_around_origin(np.array([size-1, 2, 0]), rotation_angle)
    position=position.astype(int)
    editor.placeBlock(position, Block("air"))
    # editor.placeBlock(starting_pos + np.array([size-1, 2, 0]), Block("air"))

    pos=local_pos+rotate_point_around_origin([size-2, 1, 0], rotation_angle)
    pos=pos.astype(int)
    grid.set_grid(pos[0],pos[2],3)


    position = starting_pos +rotate_point_around_origin(np.array([size-2, 1, 0]), rotation_angle)
    position=position.astype(int)
    door_dir=rotate_direction("west", rotation_angle)
    editor.placeBlock(position, Block(f'spruce_door[facing={door_dir} ,half=lower,hinge=left]'))

    roof_pos=starting_pos + np.array([0, floor_height, 0])

    # Build the roof
    if biome == "plain_biome" or biome == "jungle_biome":
        roof_block_type = random.choice(["minecraft:acacia_planks", "minecraft:dark_oak_planks"])
    if biome == "snow_biome":
        roof_block_type = random.choice(["blue_ice", "quartz_block", "bricks"])
    if biome == "desert_biome":
        roof_block_type = random.choice(["sandstone", "red_sandstone", "crying_obsidian"])
    
    roof_size=size+1
    for y in range(10):
        for i in range(roof_size-y):
            for j in range(-roof_size + i + 1+y, roof_size - i-y):
                if j == -roof_size + i + 1+y or j == roof_size - i - 1-y:
                    position = roof_pos + np.array([j, y, i])
                    editor.placeBlock(position, Block(roof_block_type))

    # Build the reflection of the roof
        for i in range(roof_size-y):
            for j in range(-roof_size + i + 1+ y, roof_size - i-y):
                if j == -roof_size + i + 1+y or j == roof_size - i - 1-y:
                    position = roof_pos + np.array([j, y, -i])
                    editor.placeBlock(position, Block(roof_block_type))

starting_pos = buildArea.begin
wall_block_type = 'stone_bricks'
roof_block_type = 'stone'
floor_block_type = 'oak_planks'
window_block_type = 'glass_pane'
staircase_block_type = 'oak_stairs'
# make_archerTower(editor, starting_pos, wall_block_type, roof_block_type, floor_block_type, window_block_type, staircase_block_type)

roof_starting_pos = buildArea.begin + np.array([0, 0, 0])
# editor.placeBlock(roof_starting_pos, Block("minecraft:cobblestone"))
    # Set the height of the pyramid
# height = 4
    # roof_starting_pos =buildArea.begin+np.array([0,0,0])


# Call the function to create the pyramid and its reflection in Minecraft
#archer_tower(editor, roof_starting_pos, block_type)


from Grid import Grid

# grid=Grid(100,100)
# grid_local=[0,0,0]
# archer_tower(editor,buildArea.begin,"plain_biome",8,grid,grid_local)
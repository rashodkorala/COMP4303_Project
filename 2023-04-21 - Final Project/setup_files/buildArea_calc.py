
import numpy as np
from gdpc import __url__, Editor, Block, geometry
from gdpc.exceptions import InterfaceConnectionError, BuildAreaNotSetError
from gdpc.vector_tools import addY


import sys
sys.path.append("setup_files")
from clearArea_calc import *


def create_editor():

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
    
    if editor.checkConnection():
        print("Connected to GDMC HTTP interface.")
    return editor



def get_world_slice (editor):

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

    if editor.getBuildArea():
        print("Build area set!")
        return worldSlice, buildRect, buildArea






def get_heightmap(buildRect, worldSlice, buildArea):

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

    #print(f"Available heightmaps: {worldSlice.heightmaps.keys()}")

    

    #print(f"Heightmap shape: {heightmap.shape}")
    heightmap = worldSlice.heightmaps["WORLD_SURFACE"]
    return heightmap


def set_build_area():
    # setting up build area and heightmap
    print("Setting up build area and heightmap...")
    editor = create_editor()
    world_slice, build_rect, build_area = get_world_slice(editor)
    heightmap = get_heightmap(build_rect, world_slice, build_area)
    print("clearing build area...")
    clear_area(heightmap, build_rect, editor, build_area, world_slice)
    
    print("build area cleared!")

    # resetting heightmap, buildRect, and editor
    print("Resetting heightmap, buildRect, and editor...")
    editor = create_editor()
    world_slice, build_rect, build_area = get_world_slice(editor)
    heightmap = get_heightmap(build_rect, world_slice, build_area)

    return editor, world_slice, build_rect, build_area, heightmap

def set_cleared_area():
    # setting up build area and heightmap
    print("Setting up build area and heightmap...")
    editor = create_editor()
    world_slice, build_rect, build_area = get_world_slice(editor)
    heightmap = get_heightmap(buildRect, worldSlice, buildArea)


    # clearing the build area
    print("Flattening build area...")
    flatten_area(heightmap, build_rect, editor, build_area)

    # resetting heightmap, buildRect, and editor
    print("Resetting heightmap, buildRect, and editor...")
    editor = create_editor()
    world_slice, build_rect, build_area = get_world_slice(editor)
    heightmap = get_heighmap(build_rect, world_slice, build_area)

    return editor, world_slice, build_rect, build_area, heightmap

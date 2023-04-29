#!/usr/bin/env python3
import random
from barracks import *
from archer_tower import *
from bunker import *
from townhall import *
from farm import *  

import sys
import numpy as np
from gdpc import __url__, Editor, Block, geometry
from gdpc.exceptions import InterfaceConnectionError, BuildAreaNotSetError
from gdpc.vector_tools import addY
def main():

        """
            Load and use a world slice.
        """

        


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

        from Grid import Grid


        # Create a grid object.
        grid = Grid(buildArea.size.x, buildArea.size.z)
        grid.print_grid()

        def getlocal(point):
            local_pos=[point[0]-buildRect._offset[0],0,point[2]-buildRect._offset[1]]
            return local_pos
        for point in buildRect.outline:
            
            height = heightmap[tuple(point - buildRect.offset)]

            #building a wall
            
            for y in range(height, height + 5):
                # Place the first layer of blocks
                point_with_offset = addY(point, y)
                local_pos=getlocal(point_with_offset)
                grid.set_grid(local_pos[0],local_pos[2],1)
                editor.placeBlock(addY(point, y), Block("cobblestone")) 
                editor.placeBlock(addY(point, y+1), Block("stone"))
                editor.placeBlock(addY(point, y+2), Block("mossy_cobblestone"))
                editor.placeBlock(addY(point, y+3), Block("mossy_cobblestone"))
                editor.placeBlock(addY(point, y+4), Block("lantern"))
                # Place the second layer of blocks
                #editor.placeBlock(addY(point+1, height+8), Block("mossy_stone_bricks"))
            


        bottom = worldSlice.heightmaps["MOTION_BLOCKING_NO_LEAVES"]
        top = worldSlice.heightmaps["WORLD_SURFACE"]
        STARTX= buildRect._offset[0]
        STARTZ= buildRect._offset[0]+ buildRect.size[0]
        ENDX=buildRect._offset[1]
        ENDZ= buildRect._offset[1] + buildRect.size[1]


        print(STARTX,STARTZ,ENDX,ENDZ)
        


        # Other code here
        def get_barracks_dimensions():
            
            house_width = random.choice([6,8])
        
            return house_width

        def get_archer_tower_dimensions():
            size = random.choice([4, 6])
            
            return size

        def get_bunker_dimensions():
            width = random.randint(3, 5)
            
            return width

        def get_farm_dimensions():
            width = random.randint(4, 8)
            
            return width

        def get_townhall_dimensions():
            width = 10
            
            return width




        # Define the structure's dimensions
        house_structure_width = get_barracks_dimensions()
        archer_tower_size = get_archer_tower_dimensions()
        bunker_underground_height = get_bunker_dimensions()
        farm_structure_width = get_farm_dimensions()
        townhall_structure_width = get_townhall_dimensions()

    # Set the number of structures to place
        num_barracks_structures = random.randint(1,3)
        num_archer_tower_structures = random.randint(1,3)
        num_bunker_structures = random.randint(1,2)
        num_farm_structures = random.choice([1,2])
        num_townhall_structures = 1
        buffer_distance = 10


        def will_overlap(grid, position, structure_width, structure_length,center=True):
            """
            Check if a new building's position would overlap with other buildings.

            :param grid: Grid object representing the world
            :param position: tuple (x, z) of the new building's top-left corner
            :param structure_width: width of the new building
            :param structure_length: length of the new building
            :return: True if the new building would overlap with other buildings, False otherwise
            """
            #everything except bunker and townhall
            if center:
                x,y,z = position
                half_width = structure_width // 2
                half_length = structure_length // 2

                top_left_x = x - half_width
                top_left_z = z - half_length

                for i in range(top_left_x, top_left_x + structure_width):
                    for j in range(top_left_z, top_left_z + structure_length):
                        if grid.is_oob(i, j) or grid.get_grid(i, j) == 1 or grid.get_grid(i, j) == 4:
                            return True
            
            else:
                x, z = position
                for i in range(x, x + structure_width):
                    for j in range(z, z + structure_length):
                        if grid.is_oob(i, j) or grid.get_grid(i, j) == 1 or grid.get_grid(i,j)==4:
                            return True
            
            return False


        # Function to generate a random position for the structure
        def generate_random_position(structure_width):
            random_x = random.randint(buildRect._offset[0]+buffer_distance, buildRect._offset[0] + buildRect.size[0] - structure_width+buffer_distance)
            random_z = random.randint(buildRect._offset[1]+buffer_distance, buildRect._offset[1] + buildRect.size[1] - structure_width+buffer_distance)
            height = worldSlice.heightmaps["MOTION_BLOCKING_NO_LEAVES"][(random_x - buildRect._offset[0], random_z - buildRect._offset[1])]
            return (random_x, height, random_z)

        # Place the structures at random locations
        biome = "plains"  # Replace this with the biome detected by your algorithm

        starting_pos = buildArea.begin
        wall_block_type = 'stone_bricks'
        roof_block_type = 'stone'
        floor_block_type = 'oak_planks'
        window_block_type = 'glass_pane'
        staircase_block_type = 'oak_stairs'

        for _ in range(num_townhall_structures):
            random_center = generate_random_position(townhall_structure_width)
            local_pos= getlocal(random_center)
            print(local_pos)
            # townhall(editor,random_center,biome,grid,townhall_structure_width)
            is_overlap=will_overlap(grid,local_pos,townhall_structure_width,townhall_structure_width)
            print(is_overlap)

            while is_overlap:
                random_center = generate_random_position(townhall_structure_width)
                local_pos= getlocal(random_center)
                is_overlap=will_overlap(grid,local_pos,townhall_structure_width,townhall_structure_width)
                print(is_overlap)
                if grid.get_grid(local_pos[0],local_pos[2])==4 or grid.get_grid(local_pos[0],local_pos[2])==1 or grid.get_grid(local_pos[0],local_pos[2])==2:
                    break
            townhall(editor,random_center,wall_block_type, roof_block_type, floor_block_type, window_block_type,grid,local_pos) 

        for _ in range(num_bunker_structures):
            random_center = generate_random_position(bunker_underground_height)
            local_pos= getlocal(random_center)
            print(local_pos)
            # barracks(editor,random_center,biome,grid,house_structure_width)
            is_overlap=will_overlap(grid,local_pos,bunker_underground_height,bunker_underground_height)
            print(is_overlap)

            while is_overlap:
                random_center = generate_random_position(bunker_underground_height)
                local_pos= getlocal(random_center)
                is_overlap=will_overlap(grid,local_pos,bunker_underground_height,bunker_underground_height)
                print(is_overlap)
                if grid.get_grid(local_pos[0],local_pos[2])==4 or grid.get_grid(local_pos[0],local_pos[2])==1 or grid.get_grid(local_pos[0],local_pos[2])==2 or grid.get_grid(local_pos[0],local_pos[2])==3:
                    is_overlap=True
            bunker(editor, random_center, biome, bunker_underground_height, grid, local_pos)

        for _ in range(num_barracks_structures):
            random_center = generate_random_position(house_structure_width)
            local_pos= getlocal(random_center)
            print(local_pos)
            # barracks(editor,random_center,biome,grid,house_structure_width)
            is_overlap=will_overlap(grid,local_pos,house_structure_width,house_structure_width)
            print(is_overlap)

            while is_overlap:
                random_center = generate_random_position(house_structure_width)
                local_pos= getlocal(random_center)
                is_overlap=will_overlap(grid,local_pos,house_structure_width,house_structure_width,False)
                print(is_overlap)
                if grid.get_grid(local_pos[0],local_pos[2])==4 or grid.get_grid(local_pos[0],local_pos[2])==1 or grid.get_grid(local_pos[0],local_pos[2])==2 or grid.get_grid(local_pos[0],local_pos[2])==3:
                    is_overlap=True
            barracks(editor,random_center,biome,grid,house_structure_width,local_pos)


        for _ in range(num_archer_tower_structures):
            random_center = generate_random_position(archer_tower_size)
            local_pos= getlocal(random_center)
            print(local_pos)
            # barracks(editor,random_center,biome,grid,house_structure_width)
            is_overlap=will_overlap(grid,local_pos,archer_tower_size,archer_tower_size)
            print(is_overlap)

            while is_overlap:
                random_center = generate_random_position(archer_tower_size)
                local_pos= getlocal(random_center)
                is_overlap=will_overlap(grid,local_pos,archer_tower_size,archer_tower_size)
                print(is_overlap)
                if grid.get_grid(local_pos[0],local_pos[2])==4 or grid.get_grid(local_pos[0],local_pos[2])==1 or grid.get_grid(local_pos[0],local_pos[2])==2 or grid.get_grid(local_pos[0],local_pos[2])==3:
                    is_overlap=True
            archer_tower(editor,random_center,biome,archer_tower_size,grid,local_pos)



        for _ in range(num_farm_structures):
            random_center =  generate_random_position(farm_structure_width)
            local_pos= getlocal(random_center)
            print(local_pos)
            # barracks(editor,random_center,biome,grid,house_structure_width)
            is_overlap=will_overlap(grid,local_pos,farm_structure_width,farm_structure_width)
            print(is_overlap)
            while is_overlap:
                random_center =  generate_random_position(farm_structure_width)
                local_pos= getlocal(random_center)
                is_overlap=will_overlap(grid,local_pos,farm_structure_width,farm_structure_width)
                print(is_overlap)
                if grid.get_grid(local_pos[0],local_pos[2])==4 or grid.get_grid(local_pos[0],local_pos[2])==1 or grid.get_grid(local_pos[0],local_pos[2])==2 or grid.get_grid(local_pos[0],local_pos[2])==3:
                    is_overlap=True
            farm(editor, random_center, farm_structure_width, grid, local_pos)






        from Grid import a_star_search,build_paths_from_grid
        # for i in range(20):
        #     center=generate_random_position(archer_tower_size)
        #     local_pos= getlocal(center)
        #     is_overlap=will_overlap(grid,local_pos,archer_tower_size,archer_tower_size)
        #     print(is_overlap)
        #     if not is_overlap:
        #         # archer_tower(editor,center,biome,grid,archer_tower_size)
        #         archer_tower(editor,center,biome,)
        #     else:
        #         editor.placeBlock(center, Block("dirt"))
        grid.print_grid()
        goals=grid.get_goals()
        start=goals[0]
        print("start",start)


        previus_goal=start

        #find path from start to end
        for goal in goals:
            path = a_star_search(grid, start, goal)
            if path is not None:
                for x, z in path:
                    grid.set_grid(x, z, 2)
                previus_goal=goal
            else:
                print("No path found")
        time.sleep(5)
        grid.print_grid()

        build_paths_from_grid(editor, grid,Block("spruce_planks"),[STARTX,-1,ENDX],heigtmap=heightmap)



        #brracks 

import sys
sys.path.append("setup_files")

from buildArea_calc import *





#Setting up editor
#Setting up build area and heightmap
#Flattening the build area
editor, world_slice, build_rect, build_area, heightmap = set_cleared_area()




# Placing walls
print("Placing walls...")
for point in build_rect.outline:
    height = heightmap[tuple(point - build_rect.offset)]
    #building a wall
    for y in range(height, height+9):
        # Place the first layer of blocks
        editor.placeBlock(addY(point, y), Block("cobblestone")) 
    








#create structure
sys.path[0] = sys.path[0].removesuffix('\\biomes\\grass')
from build_nbt_structure import *

print("Placing townhall...")
grass_townhall = "C:/Users/vilak/Desktop/Folders/2022-2023/CS4303 Assignment files/COMP4303_Project/2023-04-21 - Final Project/biomes/grass/grass_structures/grass_townhall.nbt"

create_nbt_structure(grass_townhall, editor, build_area)

#maybe make a list of all nbt structures and loop throught them each

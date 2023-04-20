import sys
sys.path.append("setup_files")

from buildArea_calc import *



editor = create_editor()
world_slice, build_rect, build_area = get_world_slice(editor)
heightmap = get_build_area(build_rect, world_slice, build_area)


#Setting up editor
#Setting up build area and heightmap
#Flattening the build area
#editor, world_slice, build_rect, build_area, heightmap = set_cleared_area()




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
from nbt_setup import *
print("Placing townhall...")






folder_path = 'biomes\grass\grass_structures' # replace with the actual folder path


file_paths = get_files(folder_path)
print(file_paths)
build_area_size = build_area.size #returns a ivec3 


for building in file_paths:    
    
    building.width, building.height, building.depth = get_building_dimensions(building)
    create_nbt_structure(building, editor, build_area, 5, 5, skips_air=True)

#maybe make a list of all nbt structures and loop throught them each

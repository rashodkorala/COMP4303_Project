import sys
sys.path.append("setup_files")

from buildArea_calc import *



editor, world_slice, build_rect, build_area, heightmap = set_build_area()

#Setting up editor
#Setting up build area and heightmap
#Flattening the build area
#editor, world_slice, build_rect, build_area, heightmap = set_cleared_area()


# Create village
sys.path[0] = sys.path[0].removesuffix('\\biomes\\grass')
from structures_setup import *
""" # Placing walls
print("Placing walls...")
for point in build_rect.outline:
    height = heightmap[tuple(point - build_rect.offset)]
    #building a wall
    create_nbt_structure() """
    
        


      






folder_path = 'biomes\grass\grass_structures' # replace with the actual folder path
file_paths = get_files(folder_path)
build_area_size = build_area.size
draw_buildings = True
placed_buildings = place_or_get_buildings(draw_buildings, file_paths, build_area_size, build_area, editor)
#draw_roads = draw_roads(file_paths, build_area_size, build_area, editor)

print(placed_buildings)
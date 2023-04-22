

import sys
sys.path.append("setup_files")

from buildArea_calc import *


editor, world_slice, build_rect, build_area, heightmap = set_build_area()

#Setting up editor
#Setting up build area and heightmap
#Flattening the build area
#editor, world_slice, build_rect, build_area, heightmap = set_cleared_area()




# Placing walls
print("Placing walls...")
for point in build_rect.outline:
    height = heightmap[tuple(point - build_rect.offset)]
    #building a wall
    for y in range(height, height + 5):
        editor.placeBlock(point + np.array([0, y, 0]), Block("sandstone"))
        editor.placeBlock(point + np.array([0, y, 1]), Block("red_sandstone"))
        editor.placeBlock(point + np.array([1, y, 0]), Block("sandstone"))
        editor.placeBlock(point + np.array([1, y, 1]), Block("red_sandstone"))
        editor.placeBlock(point + np.array([0, y, -1]), Block("torch"))
        
        


      



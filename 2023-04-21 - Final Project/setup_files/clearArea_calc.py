from gdpc import __url__, Editor, Block, geometry
from gdpc.vector_tools import addY



#flattens the area with the absolute minimum height
def flatten_area(heightmap, buildRect, editor,build_area):
    min=build_area.begin[1]
    max = build_area.size[1]+min
    
    print("max height is: ", max)
    print("min height is: ", min)

    for x in range(buildRect._offset[0], buildRect._offset[0] + buildRect.size[0]):
        for z in range(buildRect._offset[1], buildRect._offset[1] + buildRect.size[1]):
            for y in range(max, min-1,-1):
                editor.placeBlock((x, y, z), Block("air"))


    print("Build area flattened!")



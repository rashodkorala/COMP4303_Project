from gdpc import __url__, Editor, Block, geometry
from gdpc.vector_tools import addY

def clear_area(heightmap, buildRect, editor):


    print("Clearing build area...")
   
    #get min max height
    min_height = heightmap.min() + 6
    max_height = heightmap.max() + 6
    print(max_height, min_height)
    

    #get build area
    for x in range(buildRect._offset[0], buildRect._offset[0] + buildRect.size[0]):
        for z in range(buildRect._offset[1], buildRect._offset[1] + buildRect.size[1]):
            
            for y in range(min_height, max_height + 1):
                
                #clear block
                editor.placeBlock((x, y, z), Block("air"))  


    """  print("Placing the floor...")

    floor_block = Block("air")

    for x in range(buildRect._offset[0], buildRect._offset[0] + buildRect.size[0]):
        for z in range(buildRect._offset[1], buildRect._offset[1] + buildRect.size[1]):
            height = heightmap[(x - buildRect._offset[0], z - buildRect._offset[1])]
            for y in range(height):
                position = addY((x, z), y)
                editor.placeBlock(position, floor_block) """
                
    print("Build area cleared!")

    
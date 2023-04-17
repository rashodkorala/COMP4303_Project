def clear_area():
    print("Clearing build area...")

    #get min max height
    min_height = heightmap.min()
    max_height = heightmap.max()

    #get build area
    for x in range(buildRect._offset[0], buildRect._offset[0] + buildRect.size[0]):
        for z in range(buildRect._offset[1], buildRect._offset[1] + buildRect.size[1]):
            for y in range(max_height, min_height - 1, -1):

                #clear block
                editor.placeBlock((x, y, z), Block("air"))
                
    print("Build area cleared!")
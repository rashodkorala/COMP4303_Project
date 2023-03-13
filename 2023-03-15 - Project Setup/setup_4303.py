from gdpc import Editor, Block, geometry

editor = Editor(buffering=True)



# Write letter C with stone
editor.placeBlock((0,200,0), Block("stone"))
editor.placeBlock((1,200,0), Block("stone"))
editor.placeBlock((2,200,0), Block("stone"))
editor.placeBlock((2,200,1), Block("stone"))
editor.placeBlock((2,200,2), Block("stone"))
editor.placeBlock((2,200,3), Block("stone"))
editor.placeBlock((2,200,4), Block("stone"))
editor.placeBlock((1,200,4), Block("stone"))
editor.placeBlock((0,200,4), Block("stone"))



# Build a cube
geometry.placeCuboid(editor, (0,80,2), (2,82,4), Block("oak_planks"))
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

# Write letter S with stone
editor.placeBlock((-2,200,4), Block("stone"))
editor.placeBlock((-3,200,4), Block("stone"))
editor.placeBlock((-4,200,4), Block("stone"))
editor.placeBlock((-2,200,3), Block("stone"))
editor.placeBlock((-2,200,2), Block("stone"))
editor.placeBlock((-3,200,2), Block("stone"))
editor.placeBlock((-4,200,2), Block("stone"))
editor.placeBlock((-4,200,1), Block("stone"))
editor.placeBlock((-4,200,0), Block("stone"))
editor.placeBlock((-3,200,0), Block("stone"))
editor.placeBlock((-2,200,0), Block("stone"))

# Write number 4 with stone
editor.placeBlock((-9,200,4), Block("stone"))
editor.placeBlock((-9,200,3), Block("stone"))
editor.placeBlock((-9,200,2), Block("stone"))
editor.placeBlock((-9,200,1), Block("stone"))
editor.placeBlock((-9,200,0), Block("stone"))
editor.placeBlock((-7,200,2), Block("stone"))
editor.placeBlock((-8,200,2), Block("stone"))
editor.placeBlock((-6,200,2), Block("stone"))
editor.placeBlock((-6,200,3), Block("stone"))
editor.placeBlock((-6,200,4), Block("stone"))

#write number 3 with stone
editor.placeBlock((-11,200,4), Block("stone"))
editor.placeBlock((-12,200,4), Block("stone"))
editor.placeBlock((-13,200,4), Block("stone"))
editor.placeBlock((-13,200,3), Block("stone"))
editor.placeBlock((-13,200,2), Block("stone"))
editor.placeBlock((-12,200,2), Block("stone"))
editor.placeBlock((-11,200,2), Block("stone"))
editor.placeBlock((-13,200,1), Block("stone"))
editor.placeBlock((-11,200,0), Block("stone"))
editor.placeBlock((-12,200,0), Block("stone"))
editor.placeBlock((-13,200,0), Block("stone"))

#write number 0 with stone
editor.placeBlock((-15,200,4), Block("stone"))
editor.placeBlock((-16,200,4), Block("stone"))
editor.placeBlock((-17,200,4), Block("stone"))
editor.placeBlock((-15,200,0), Block("stone"))
editor.placeBlock((-16,200,0), Block("stone"))
editor.placeBlock((-17,200,0), Block("stone"))
editor.placeBlock((-15,200,1), Block("stone"))
editor.placeBlock((-15,200,2), Block("stone"))
editor.placeBlock((-15,200,3), Block("stone"))
editor.placeBlock((-17,200,1), Block("stone"))
editor.placeBlock((-17,200,2), Block("stone"))
editor.placeBlock((-17,200,3), Block("stone"))

#write number 3 with stone
editor.placeBlock((-19,200,4), Block("stone"))
editor.placeBlock((-20,200,4), Block("stone"))
editor.placeBlock((-21,200,4), Block("stone"))
editor.placeBlock((-21,200,3), Block("stone"))
editor.placeBlock((-21,200,2), Block("stone"))
editor.placeBlock((-20,200,2), Block("stone"))
editor.placeBlock((-19,200,2), Block("stone"))
editor.placeBlock((-21,200,1), Block("stone"))
editor.placeBlock((-19,200,0), Block("stone"))
editor.placeBlock((-20,200,0), Block("stone"))
editor.placeBlock((-21,200,0), Block("stone"))






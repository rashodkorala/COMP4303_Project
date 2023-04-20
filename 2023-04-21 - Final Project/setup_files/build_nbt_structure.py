from structures.nbt.convert_nbt import convert_nbt
from structures.nbt.nbt_asset import NBTAsset
from structures.structure import Structure
from structures.transformation import Transformation
from gdpc.editor import Editor
from gdpc.block import Block
from palette.palette import Palette
from palette.palette_swap import palette_swap


def create_nbt_structure(filepath, editor, buildArea):
    structure = convert_nbt(filepath)

    #create nbt structure
    for (pos, palette_index) in structure.blocks.items():
        block = structure.palette[palette_index]
        build_pos = buildArea.begin + pos
        editor.placeBlock(position=build_pos, block=block.to_gdpc_block())
        #print(build_pos, block.to_gdpc_block())

    
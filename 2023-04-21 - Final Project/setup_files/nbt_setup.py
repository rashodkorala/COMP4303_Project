from structures.nbt.convert_nbt import convert_nbt
from structures.nbt.nbt_asset import NBTAsset
from structures.structure import Structure
from structures.transformation import Transformation
from gdpc.editor import Editor
from gdpc.block import Block
from palette.palette import Palette
from palette.palette_swap import palette_swap
import os

# returns the dimensions of the structure
def get_building_dimensions(filepath):
    structure = convert_nbt(filepath)
    return structure.width, structure.height, structure.depth 


#creates the structure from the nbt file
def create_nbt_structure(filepath, editor, buildArea, x, z, skips_air=True):
    structure = convert_nbt(filepath)

    #create nbt structure
    for (pos, palette_index) in structure.blocks.items():
        block = structure.palette[palette_index]
        if block.to_gdpc_block().id == "minecraft:air" and skips_air:
            continue
        build_pos = buildArea.begin + pos+[x,0,z]
        editor.placeBlock(position=build_pos, block=block.to_gdpc_block())
        #print(build_pos, block.to_gdpc_block())


#gets the nbt files in the folder
def get_files(folder_path):
    file_paths = []

    for foldername, subfolders, filenames in os.walk(folder_path):
        for filename in filenames:
            # get the relative path of the file
            relative_path = os.path.join(foldername, filename)[len(folder_path)+1:]
            file_paths.append(relative_path)
    return file_paths


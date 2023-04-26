from structures.nbt.convert_nbt import convert_nbt
from structures.nbt.nbt_asset import NBTAsset
from structures.structure import Structure
from structures.transformation import Transformation
from gdpc.editor import Editor
from gdpc.block import Block
from palette.palette import Palette
from palette.palette_swap import palette_swap
import os
import random
from gdpc import __url__, Editor, Block, geometry


# returns the dimensions of the structure
def get_building_dimensions(filepath):
    structure = convert_nbt(filepath)
    return structure.width, structure.height, structure.depth 


# Check if a building overlaps with any other existing buildings
def is_overlapping(new_building, existing_buildings, gap=5):
    for building in existing_buildings:
        if not (new_building["x"] + new_building["width"] + gap <= building["x"] or
                new_building["x"] >= building["x"] + building["width"] + gap or
                new_building["z"] + new_building["depth"] + gap <= building["z"] or
                new_building["z"] >= building["z"] + building["depth"] + gap):
            return True
    return False



# Generate random building position within the build area
def random_building_position(building_width, building_depth, build_area_size):
    x = random.randint(0, build_area_size.x- 4 - building_width)
    z = random.randint(0, build_area_size.z- 4 - building_depth)
    return x, z



def random_building_transformation():
    mirror_x = bool(random.getrandbits(1))
    mirror_z = bool(random.getrandbits(1))

    transformation = Transformation(
        mirror=(mirror_x, False, mirror_z),
    )

    return transformation


 


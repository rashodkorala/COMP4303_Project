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


""" #creates the structure from the nbt file
def create_nbt_structure(filepath, editor, buildArea, x, z, skips_air=True):
    structure = convert_nbt(filepath)
    transformation = random_building_transformation()
    transformed_palette = transformation.apply_to_palette(structure.palette)

    #create nbt structure
    for (pos, palette_index) in structure.blocks.items():
        block = transformed_palette[palette_index]



        build_pos = buildArea.begin + pos+[x,0,z]
        x, y, z = transformation.apply_to_point(
            point=pos,
            structure=structure,
            asset= asset
        )
        editor.placeBlock(position=build_pos, block=block.to_gdpc_block())
        #print(build_pos, block.to_gdpc_block()) """

def create_nbt_structure(filepath, editor, build_area, x, z, skips_air=True):
    structure = convert_nbt(filepath)

    #create nbt structure
    for (pos, palette_index) in structure.blocks.items():
        block = structure.palette[palette_index]
        if block.to_gdpc_block().id == "minecraft:air" and skips_air:
            continue
        build_pos = build_area.begin + pos + [x,0,z]
        editor.placeBlock(position=build_pos, block=block.to_gdpc_block())
        #print(build_pos, block.to_gdpc_block())

def get_files(folder_path):
    file_paths = []

    for foldername, subfolders, filenames in os.walk(folder_path):
        for filename in filenames:
            if filename.endswith('.nbt'):
                full_path = os.path.join(foldername, filename)
                file_paths.append(full_path)
               

    return file_paths



# Check if a building overlaps with any other existing buildings
def is_overlapping(new_building, existing_buildings):
    for building in existing_buildings:
        if not (new_building["x"] + new_building["width"] <= building["x"] or
                new_building["x"] >= building["x"] + building["width"] or
                new_building["z"] + new_building["depth"] <= building["z"] or
                new_building["z"] >= building["z"] + building["depth"]):
            return True
    return False


# Generate random building position within the build area
def random_building_position(building_width, building_depth, build_area_size):
    x = random.randint(0, build_area_size.x - building_width)
    z = random.randint(0, build_area_size.z - building_depth)
    return x, z



def random_building_transformation():
    mirror_x = bool(random.getrandbits(1))
    mirror_z = bool(random.getrandbits(1))

    transformation = Transformation(
        mirror=(mirror_x, False, mirror_z),
    )

    return transformation



def place_or_get_buildings(draw, file_paths, build_area_size, build_area, editor, max_attempts=100):
    existing_buildings = []
    
    for building in file_paths:
        building_width, building_height, building_depth = get_building_dimensions(building)
        
        is_townhall = "townhall" in os.path.basename(building)

        if not is_townhall:
            # Generate random number of building placements
            building_number = random.randint(2, 3)
        else:
            print("Townhall found: ", building)
            building_number = 1

        # Try to find a non-overlapping position for the building
        for i in range(building_number):
            attempts = 0
            while attempts < max_attempts:
                x, z = random_building_position(building_width, building_depth, build_area_size)
                new_building = {"x": x, "z": z, "width": building_width, "depth": building_depth}

                if not is_overlapping(new_building, existing_buildings):
                    existing_buildings.append(new_building)
                    if draw:
                        create_nbt_structure(building, editor, build_area, x, z, skips_air=True)
                    break

                attempts += 1

            if attempts == max_attempts:
                print(f"Failed to place {building} without overlapping after {max_attempts} attempts.")

    return existing_buildings



import networkx as nx
import sys
sys.path.append("setup_files")
from structures_setup import *

def draw_roads(file_paths, build_area_size, build_area, editor):
    draw_buildings = False
    existing_buildings = place_or_get_buildings(draw_buildings, file_paths, build_area_size, build_area, editor)
        
    # Step 1: Identify the locations of each building
    building_positions = [(building["x"], building["z"]) for building in existing_buildings]

    # Step 2: Define a graph
    G = nx.Graph()
    G.add_nodes_from(building_positions)

    # Define edges between buildings that are close to each other
    for i in range(len(building_positions)):
        for j in range(i+1, len(building_positions)):
            dist = abs(building_positions[i][0]-building_positions[j][0]) + \
                abs(building_positions[i][1]-building_positions[j][1])

            # If the distance between two buildings is less than 15, add an edge (ultimately, a road)
            if dist < 100:
                G.add_edge(building_positions[i], building_positions[j])



    """ 
    # Step 3: Implement pathfinding algorithm
    paths = {}
    for i in range(len(building_positions)):
        for j in range(i+1, len(building_positions)):
            try:
                path = nx.shortest_path(G, source=building_positions[i], target=building_positions[j])
                paths[(building_positions[i], building_positions[j])] = path
                print(f"Path between {building_positions[i]} and {building_positions[j]}: {path}")
            except nx.NetworkXNoPath:
                print(f"No path between {building_positions[i]} and {building_positions[j]}")

    # Step 4: Place roads on the map
    
    road_block = Block("minecraft:gravel")
    for path in paths.values():
        for i in range(len(path)-1):
            x1, z1 = path[i]
            x2, z2 = path[i+1]
            if x1 == x2:
                for z in range(min(z1, z2), max(z1, z2)):
                    print("x1==x2", build_area.begin + [x1,0,z])
                    editor.placeBlock(position=build_area.begin + [x1,0,z], block=road_block)
            elif z1 == z2:
                for x in range(min(x1, x2), max(x1, x2)):
                    print("z1==z2", build_area.begin + [x,0,z1])
                    editor.placeBlock(position=build_area.begin + [x,0,z1], block=road_block)
            else:
                print("x1 != x2 and z1 != z2", build_area.begin + [x1,0,z1])
                editor.placeBlock(position=build_area.begin + [x1,0,z1], block=road_block) """


import math
import os
import json
import logging

from copy import deepcopy

import numpy as np
import pandas as pd
from shapely.geometry import Point
import pyproj

# projection param
geod = pyproj.Geod(ellps='WGS84')


def get_grid_cell_id(idx, idy):
    return str(idx) + "_" + str(idy)


def construct(x_min, y_min, x_max, y_max, cell_size=1000):
    '''
    Creating grid
    '''

    logging.info("Creating grid...")

    # create corners of rectangle to be transformed to a grid
    min_corner = Point((x_min, y_min))
    max_corner = Point((x_max, y_max))

    # get the centroid of the cell left-down from the grid min corner; that is the origin of the grid
    origin = geod.fwd(min_corner.x, min_corner.y, -135, cell_size / math.sqrt(2))
    origin = Point(origin[0], origin[1])

    # get the centroid of the cell right-up from the grid max corner; that is the final point of the grid
    final = geod.fwd(max_corner.x, max_corner.y, 45, cell_size / math.sqrt(2))
    final = Point(final[0], final[1])

    fwdax, backax, dx = geod.inv(origin.x, origin.y, final.x, origin.y)
    fwday, backay, dy = geod.inv(origin.x, origin.y, origin.x, final.y)

    # construct grid
    x = origin.x
    y = origin.y

    current_point = deepcopy(origin)
    grid_id_2_cell_id = {}

    idx = 0

    cell_id = 0
    grid_lons = []
    grid_lats = []

    gcids = []
    while x < final.x:
        y = origin.y
        idy = 0

        while y < final.y:
            y = geod.fwd(current_point.x, y, fwday, cell_size)[1]
            current_point = Point(x, y)

            grid_lats.append(current_point.y)
            grid_lons.append(current_point.x)

            grid_id = get_grid_cell_id(idx, idy)
            grid_id_2_cell_id[grid_id] = cell_id

            cell_id += 1
            gcids.append(cell_id)
            idy += 1

        x = geod.fwd(current_point.x, current_point.y, fwdax, cell_size)[0]
        current_point = Point(x, current_point.y)
        idx += 1

    grid = pd.DataFrame(data=grid_lats, index=np.arange(len(grid_lats)), columns=["lat"])
    grid["lon"] = grid_lons
    grid["gcid"] = gcids

    num_cells_x = len(set(grid_lons))
    num_cells_y = len(set(grid_lats))

    logging.info("Created grid of size")
    logging.info(str(num_cells_x) + "x" + str(num_cells_y))
    logging.info("Done.")

    return grid, grid_id_2_cell_id, origin, final


def get_bbox(data):
    logging.info("Getting bounding box...")

    x_min = min(data['lon'].to_numpy())
    x_max = max(data['lon'].to_numpy())

    y_min = min(data['lat'].to_numpy())
    y_max = max(data['lat'].to_numpy())

    logging.info("Done.")

    return x_min, y_min, x_max, y_max


def lon_lat_2_point(lon, lat):
    return Point(lon, lat)


def point_2_grid_cell_id_lookup(point, grid_id_2_cell_id, origin, cell_size=5000):
    p = lon_lat_2_point(point["lon"], point["lat"])

    fwdax, backax, dx = geod.inv(origin.x, origin.y, p.x, origin.y)
    fwday, backay, dy = geod.inv(origin.x, origin.y, origin.x, p.y)

    idx = int(dx / (cell_size + 0.0)) + 1
    idy = int(dy / (cell_size + 0.0)) + 1

    grid_id = get_grid_cell_id(idx, idy)

    if grid_id in grid_id_2_cell_id:
        cid = int(grid_id_2_cell_id[grid_id])
    else:
        cid = None

    return (cid, idx, idy)


def _create_grid_files( point_records_file_in, final_grid_files_dir, site):
    """
    Purpose: Create grid file (as csv) from records file.
    Author: pselvaraj
    """
    # create paths first...
    output_filename = f"{site}_grid.csv"
    if not os.path.exists(final_grid_files_dir):
        os.mkdir(final_grid_files_dir)
    out_path = os.path.join(final_grid_files_dir, output_filename )

    if not os.path.exists( out_path ):
        # Then manip data...
        #logging.info("Reading data...")
        print( f"{out_path} not found so we are going to create it." )
        print( f"Reading {point_records_file_in}." )
        point_records = pd.read_csv(point_records_file_in, encoding="iso-8859-1")
        point_records = point_records[~(point_records['pop'] == 0)]
        point_records.rename(columns={'longitude': 'lon', 'latitude': 'lat'}, inplace=True)

        if not 'pop' in point_records.columns:
            point_records['pop'] = [5.5] * len(point_records)

        if 'hh_size' in point_records.columns:
            point_records['pop'] = point_records['hh_size']

        # point_records = point_records[point_records['pop']>0]
        x_min, y_min, x_max, y_max = get_bbox(point_records)
        point_records = point_records[
            (point_records.lon >= x_min) & (point_records.lon <= x_max) & (point_records.lat >= y_min) & (
                    point_records.lat <= y_max)]
        gridd, grid_id_2_cell_id, origin, final = construct(x_min, y_min, x_max, y_max, cell_size=5000)
        gridd.to_csv(os.path.join(final_grid_files_dir, f"{site}_grid_interim.csv"))

        with open(os.path.join(final_grid_files_dir, f"{site}_grid_id_2_cell_id.json"), "w") as g_f:
            json.dump(grid_id_2_cell_id, g_f, indent=3)

        point_records[['gcid', 'gidx', 'gidy']] = point_records.apply(
                point_2_grid_cell_id_lookup,
                args=(grid_id_2_cell_id, origin), axis=1).apply(pd.Series)

        grid_pop = point_records.groupby(['gcid', 'gidx', 'gidy'])['pop'].apply(np.sum).reset_index()
        # grid_pop['pop'] = grid_pop['pop'].apply(lambda x: round(x/5))
        grid_final = pd.merge(gridd, grid_pop, on='gcid')
        grid_final['node_label'] = list(grid_final.index)
        grid_final = grid_final[grid_final['pop'] > 5]
        grid_final.to_csv(os.path.join(final_grid_files_dir, output_filename ))

    print( f"{out_path} gridded population file created or found." )
    return out_path
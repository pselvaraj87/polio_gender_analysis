import rasterio
from pyproj import Proj, transform
from affine import Affine
from create_grid_files import _create_grid_files
import numpy as np
import pandas as pd
import os

from raster_clipping_and_extraction_functions import run_all_clipping

data_dir = '/Users/prashanthselvaraj/Github/polio_gender_analysis/data/raster_csv'

def convert_raster_to_csv(fname):

    with rasterio.open(fname) as r:
        T0 = r.transform  # upper-left pixel corner affine transform
        p1 = Proj(r.crs)
        A = r.read()  # pixel values

    # All rows and columns
    cols, rows = np.meshgrid(np.arange(A.shape[2]), np.arange(A.shape[1]))

    # Get affine transform for pixel centres
    T1 = T0 * Affine.translation(0.5, 0.5)
    # Function to convert pixel row/column index (from 0) to easting/northing at centre
    rc2en = lambda r, c: (c, r) * T1

    # All eastings and northings (there is probably a faster way to do this)
    eastings, northings = np.vectorize(rc2en, otypes=[float, float])(rows, cols)

    # Project all longitudes, latitudes
    p2 = Proj(proj='latlong', datum='WGS84')
    longs, lats = transform(p1, p2, eastings, northings)
    values = A[0]
    values[values<0] = 0
    values = list(values.ravel())
    lats = list(lats.ravel())
    longs = list(longs.ravel())
    df = pd.DataFrame({'latitude': longs, 'longitude': lats, 'pop': values})
    df.to_csv(os.path.join(data_dir, fname.split('.')[0] + '.csv'))

    return os.path.join(data_dir, fname.split('.')[0] + '.csv')


if __name__ == '__main__':
    # tif_dir = '/Users/prashanthselvaraj/Github/polio_gender_analysis/data/pakistan_under_5'
    run_clipping = 0
    run_csv_pop_raster = 0
    run_create_grid_files = 1

    tif_dir = '/Users/prashanthselvaraj/Github/polio_gender_analysis/data/PAK_Rapid_Population_Estimate_Age_Under_5'
    grid_data = pd.read_excel('/Users/prashanthselvaraj/Github/polio_gender_analysis/data/FATA TDP ERP - Finalized Geo.xlsx')
    grid_data = grid_data[['latitude', 'longitude']]
    grid_data.dropna(subset=['latitude'], inplace=True)
    grid_data['latitude'] = grid_data['latitude'].apply(lambda x: float(x.split('°')[0]))
    grid_data['longitude'] = grid_data['longitude'].apply(lambda x: float(x.split('°')[0]))

    for file in os.listdir(tif_dir):
        if 'DS' not in file:
            shp_path = os.path.join(tif_dir, file.split('.')[0])
            os.makedirs(shp_path, exist_ok=True)
            outfilename = os.path.join(data_dir, file.split('.')[0] + '.csv')

            if run_clipping:
                rasterpath = run_all_clipping(os.path.join(tif_dir, file), out_path=tif_dir,
                                              shapefile_type='bbox', outfilename=outfilename,
                                              grid_data=grid_data, shp_outpath=shp_path, overwrite=False,
                                              alpha=0.001, out_name="raster", write_shp=True, crop=True)

            if run_csv_pop_raster:
                rasterpath = '/Users/prashanthselvaraj/Github/polio_gender_analysis/data/raster_csv/pak_rpe_2021_09_age_0_5.tif'
                csv_path = convert_raster_to_csv(rasterpath)

            if run_create_grid_files:
                csv_path = '/Users/prashanthselvaraj/Github/polio_gender_analysis/data/raster_csv/pak_rpe_2021_09_age_0_5.csv'
                _create_grid_files(csv_path, data_dir, 'KP')



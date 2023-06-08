import os
import re
import shapely.geometry
import geopandas as gpd
import rasterio
import rasterio.mask
import rasterio.plot
import matplotlib.pyplot as plt
from shapely.ops import cascaded_union, polygonize
from scipy.spatial import Delaunay
import numpy as np
import math
import pdb


def find_latlong(name_list):
    lat_idx = [i for i, j in enumerate([re.match("lat", name) for name in name_list]) if j is not None]
    lon_idx = [i for i, j in enumerate([re.match("l.*n.*g.*", name) for name in name_list]) if j is not None]

    lat_name = name_list[lat_idx][0]
    lon_name = name_list[lon_idx][0]

    return lat_name, lon_name


def alpha_shape(points, alpha):
    """
    Compute the alpha shape (concave hull) of a set
    of points.
    @param points: Iterable container of points.
    @param alpha: alpha value to influence the
        gooeyness of the border. Smaller numbers
        don't fall inward as much as larger numbers.
        Too large, and you lose everything!
    """
    if len(points) < 4:
        # When you have a triangle, there is no sense
        # in computing an alpha shape.
        return shapely.geometry.MultiPoint(list(points)).convex_hull


    def add_edge(edges, edge_points, coords, i, j):
        """
        Add a line between the i-th and j-th points,
        if not in the list already
        """
        if (i, j) in edges or (j, i) in edges:
            # already added
            return
        edges.add( (i, j) )
        edge_points.append(coords[ [i, j] ])

    coords = np.array([point.coords[0]
                       for point in points])
    tri = Delaunay(coords)
    edges = set()
    edge_points = []

    # loop over triangles:
    # ia, ib, ic = indices of corner points of the
    # triangle
    for ia, ib, ic in tri.vertices:
        pa = coords[ia]
        pb = coords[ib]
        pc = coords[ic]

        # Lengths of sides of triangle
        a = math.sqrt((pa[0]-pb[0])**2 + (pa[1]-pb[1])**2)
        b = math.sqrt((pb[0]-pc[0])**2 + (pb[1]-pc[1])**2)
        c = math.sqrt((pc[0]-pa[0])**2 + (pc[1]-pa[1])**2)

        # Semiperimeter of triangle
        s = (a + b + c)/2.0

        # Area of triangle by Heron's formula
        area = math.sqrt(s*(s-a)*(s-b)*(s-c))
        circum_r = a*b*c/(4.0*area)

        # Here's the radius filter.
        if circum_r < 1.0/alpha:
            add_edge(edges, edge_points, coords, ia, ib)
            add_edge(edges, edge_points, coords, ib, ic)
            add_edge(edges, edge_points, coords, ic, ia)
    m = shapely.geometry.MultiLineString(edge_points)
    triangles = list(polygonize(m))
    return cascaded_union(triangles), edge_points


def mask_raster(raster, mask_shapes, out_path=".", write=False, crop=True):
    """
    Clip and mask raster based on polygon shapefile border.

    :param raster: rasterio dataset to clip
    :param mask_shapes: geojson of coordinates to clip to
    :param out_path: if writing, filepath for new raster file
    :param write: boolean-- should new raster be written to file?
    :return: clipped and masked raster and metadata
    """
    out_image, out_transform = rasterio.mask.mask(raster, mask_shapes, crop=crop)
    out_meta = raster.meta.copy()
    out_meta.update({'driver': 'GTiff',
                     'height': out_image.shape[1],
                     'width': out_image.shape[2],
                     'transform': out_transform})

    if write:
        print("saving")
        with rasterio.open(out_path, 'w', **out_meta) as out_file:
            out_file.write(out_image)

    return out_image, out_meta


def make_shapefile(data, type, from_crs="default", to_crs=None, alpha=10,
                   lat_name='latitude', lon_name='longitude'):
    """
    From a dataframe of lat-longs, create a shapefile with the desired properties.

    :param data: pd.DataFrame with, at minimum, columns named "latitude" and "longitude"
    :param type: one of "point", "bbox", "buffer" "concave_hull", or "convex_hull", determining
                 whether/how to draw polygons around the points in data.
    :param from_crs: dict or string with valid geopandas coordinate reference system, see
                http://geopandas.org/projections.html. This will usually be {'init' :'epsg:4326'}
    :param to_crs: if shapefile needs to be reprojected, new crs.
    :param alpha: if type is "convex hull", determines 'tightness' of hull around points.
                  if type is "buffer", determines radius of buffer.
    :param lat_name: str, name for the latitude column
    :param lon_name: str, name for the longitude column
    :return: a geodataframe with the new shapefile points.
    """

    def make_points(data):
        data.dropna(inplace=True)
        points = [shapely.geometry.Point(xy) for xy in zip(data[lon_name], data[lat_name])]
        data.drop([lat_name, lon_name], axis=1, inplace=True)
        point_df = gpd.GeoDataFrame(data,
                                    geometry=points)
        return point_df

    if type=="point":
        shape_df = make_points(data)

    elif type=="convex_hull":
        points_df = make_points(data)
        points = points_df['geometry'].tolist()
        point_collection = shapely.geometry.MultiPoint(points)

        convex_hull = point_collection.convex_hull
        shape_df = gpd.GeoDataFrame({'geometry': [convex_hull]})

    elif type=="concave_hull":
        points_df = make_points(data)
        points = points_df['geometry'].tolist()

        concave_hull, edge_points = alpha_shape(points, alpha=alpha)
        shape_df = gpd.GeoDataFrame({'geometry': [concave_hull]})

    elif type=="bbox":
        min_x, max_x, min_y, max_y = data[lon_name].min(), data[lon_name].max(), data[lat_name].min(), data[lat_name].max()
        bounds = [(min_x-0.5, max_y+0.5), (max_x+0.5, max_y+0.5), (max_x+0.5, min_y-0.5), (min_x-0.5, min_y-0.5)]
        poly = shapely.geometry.Polygon(bounds)

        shape_df = gpd.GeoDataFrame({'geometry': [poly]})

    elif type=="buffer":
        points_df = make_points(data)
        points = points_df['geometry'].tolist()
        point_collection = shapely.geometry.MultiPoint(points)

        buffer = point_collection.buffer(distance=alpha)
        shape_df = gpd.GeoDataFrame({'geometry': [buffer]})

    else:
        raise ValueError("shapefile type " + type + " not recognized!")

    shape_df.crs = {'init' :'epsg:4326'} if from_crs=="default" else from_crs

    if to_crs:
        shape_df = shape_df.to_crs(to_crs)

    return shape_df


def run_all_clipping(raster_path, out_path, shapefile_type, outfilename,
                     grid_data, shp_outpath, overwrite=False,
                     alpha=15, out_name="raster", write_shp=True, crop=True):

    if not os.path.exists(out_path):
        os.makedirs(out_path, exist_ok=True)

    # load the first file, get projection
    print("loading raster for projection")
    in_raster = rasterio.open(raster_path)

    print("creating shapefile")

    lat_name, lon_name = find_latlong(grid_data.columns)

    shp = make_shapefile(grid_data.copy(), type=shapefile_type,
                         to_crs=in_raster.crs.to_dict(), alpha=alpha,
                         lat_name=lat_name, lon_name=lon_name)

    if write_shp:
        if not os.path.exists(shp_outpath):
            os.mkdir(shp_outpath)
        shp.to_file(shp_outpath)

    # clip  raster
    mask_shapes = [shapely.geometry.mapping(g) for g in shp['geometry']]

    print( raster_path)
    out_tif_name = outfilename.split('.')[0] + '.tif'.format(out_name=out_name)

    out_fname = os.path.join(out_path, out_tif_name)
    if os.path.isfile(out_fname) and not overwrite:
        print("clipped raster already exists")

    print("loading input raster " + raster_path)
    in_raster = rasterio.open(raster_path)
    mask_raster(in_raster, mask_shapes, out_fname, write=True, crop=crop)

    print("plotting")

    fig, axes = plt.subplots(1, 1, sharex=True, sharey=True)
    axes = [axes]

    ## collapse list if necessary
    try:
        axes_list = [item for sublist in axes for item in sublist]
    except:
        axes_list = [item for item in axes]

    to_plot = rasterio.open(out_fname)

    ax = axes_list.pop(0)

    rasterio.plot.show(to_plot, ax=ax)

    plt.savefig(os.path.join(out_path, outfilename.split('.')[0] + '.png'))

    return out_fname
# -*- coding: utf-8 -*-
"""
******************************************************************************

 Project:    SAR Drift Data converter
 Purpose:    Converter SAR drift data into visually interactive output
 Author:     Brendon Gory, brendon.gory@noaa.gov
                           brendon.gory@colostate.edu
             Data Science Application Specialist (Research Associate II)
             at CSU CIRA
 Supervisor: Dr. Prasanjit Dash, prasanjit.dash@noaa.gov
                               prasanjit.dash@colostate.edu
             CSU CIRA Research Scientist III
             (Program Innovation Scientist)
******************************************************************************
Copyright notice
         NOAA STAR SOCD and Colorado State Univ CIRA
         2025, Version 1.0.0
         POC: Brendon Gory (brendon.gory@noaa.gov)

 Permission is hereby granted, free of charge, to any person obtaining a
 copy of this software and associated documentation files (the "Software"),
 to deal in the Software without restriction, including without limitation
 the rights to use, copy, modify, merge, publish, distribute, sublicense,
 and/or sell copies of the Software, and to permit persons to whom the
 Software is furnished to do so, subject to the following conditions:

 The above copyright notice and this permission notice shall be included
 in all copies or substantial portions of the Software.

 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
 OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
 THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
 DEALINGS IN THE SOFTWARE.
"""

import os
import sys
from pathlib import Path

# Derive paths from the active env rather than hard-coding
env_prefix = Path(sys.prefix)
proj_dir = env_prefix / "Library" / "share" / "proj"
bin_dir = env_prefix / "Library" / "bin"

# print("Using PROJ dir:", proj_dir)
# print("Using bin dir:", bin_dir)

os.add_dll_directory(str(bin_dir))

# Set both env vars for PROJ
os.environ["PROJ_DATA"] = str(proj_dir)
os.environ["PROJ_LIB"] = str(proj_dir)   # backward compatibility

# Tell pyproj explicitly where proj.db lives
from pyproj.datadir import set_data_dir
set_data_dir(str(proj_dir))

from pyproj import CRS, Transformer


######################################################
# Take starting date which coressponds to Lon1, Lat1 #
######################################################

# =============================================================
# Grid navigation functions from 
# https://github.com/nsidc/polarstereo-lonlat-convert-py/blob/
# main/polar_convert/polar_convert.py
# =============================================================

# The grid size cell dimensions in km
VALID_GRID_SIZES = (6.25, 12.5, 25)

# Valid hemisphere names.
NORTH = 'north'
SOUTH = 'south'
VALID_HEMISPHERES = (NORTH, SOUTH)

# Earth-parameter defualts
TRUE_SCALE_LATITUDE = 70
EARTH_RADIUS_KM = 6378.273
EARTH_ECCENTRICITY = 0.081816153


def _validate_grid_size(grid_size):
    if grid_size not in VALID_GRID_SIZES:
        raise ValueError(
            f'Got `grid_size` of {grid_size} but expected one of '
            f'{VALID_GRID_SIZES}'
        )

    return grid_size


def _validate_hemisphere(hemisphere):
    if not isinstance(hemisphere, str) or hemisphere.lower()  \
    not in VALID_HEMISPHERES:
        raise ValueError(
            f'Got `hemisphere` of {hemisphere} but expected one of '
            f'{VALID_HEMISPHERES}'
        )

    return hemisphere.lower()


def _hemi_direction(hemisphere):
    """Return `1` for 'north' and `-1` for 'south'"""
    return {'north': 1, 'south': -1}[hemisphere]


def _grid_params(grid_size, hemisphere):
    if hemisphere == NORTH:
        delta = 45
        imax = 1216
        jmax = 1792
        xmin = -3850 + grid_size / 2
        ymin = -5350 + grid_size / 2
    else:
        delta = 0
        imax = 1264
        jmax = 1328
        xmin = -3950 + grid_size / 2
        ymin = -3950 + grid_size / 2

    if grid_size == 12.5:
        imax = imax // 2
        jmax = jmax // 2
    elif grid_size == 25:
        imax = imax // 4
        jmax = jmax // 4

    return delta, imax, jmax, xmin, ymin


def _polar_lonlat_to_xy(longitude, latitude, true_scale_lat, re, e, hemisphere):
    """Convert from geodetic longitude and latitude to Polar Stereographic
    (X, Y) coordinates in km.

    Args:
        longitude (float): longitude or longitude array in degrees
        latitude (float): latitude or latitude array in degrees (positive)
        true_scale_lat (float): true-scale latitude in degrees
        re (float): Earth radius in km
        e (float): Earth eccentricity
        hemisphere ('north' or 'south'): Northern or Southern hemisphere

    Returns:
        If longitude and latitude are scalars then the result is a
        two-element list containing [X, Y] in km.
        If longitude and latitude are numpy arrays then the result will be a
        two-element list where the first element is a numpy array containing
        the X coordinates and the second element is a numpy array containing
        the Y coordinates.
    """
    import numpy as np

    hemisphere = _validate_hemisphere(hemisphere)
    hemi_direction = _hemi_direction(hemisphere)

    lat = abs(latitude) * np.pi / 180
    lon = longitude * np.pi / 180
    slat = true_scale_lat * np.pi / 180

    e2 = e * e

    # Snyder (1987) p. 161 Eqn 15-9
    t = np.tan(np.pi / 4 - lat / 2) / \
        ((1 - e * np.sin(lat)) / (1 + e * np.sin(lat))) ** (e / 2)

    if abs(90 - true_scale_lat) < 1e-5:
        # Snyder (1987) p. 161 Eqn 21-33
        rho = 2 * re * t / np.sqrt((1 + e) ** (1 + e) * (1 - e) ** (1 - e))
    else:
        # Snyder (1987) p. 161 Eqn 21-34
        tc = np.tan(np.pi / 4 - slat / 2) / \
            ((1 - e * np.sin(slat)) / (1 + e * np.sin(slat))) ** (e / 2)
        mc = np.cos(slat) / np.sqrt(1 - e2 * (np.sin(slat) ** 2))
        rho = re * mc * t / tc

    x = rho * hemi_direction * np.sin(hemi_direction * lon)
    y = -rho * hemi_direction * np.cos(hemi_direction * lon)
    return [x, y]


def _polar_lonlat_to_ij(longitude, latitude, grid_size, hemisphere):
    
    """Transform from geodetic longitude and latitude coordinates
    to NSIDC Polar Stereographic I, J coordinates

    Args:
        longitude (float): longitude or longitude array in degrees
        latitude (float): latitude or latitude array in degrees (positive)
        grid_size (float): 6.25, 12.5 or 25; the grid_size cell dimensions in km
        hemisphere ('north' or 'south'): Northern or Southern hemisphere

    Returns:
        If longitude and latitude are scalars then the result is a
        two-element list containing [I, J].
        If longitude and latitude are numpy arrays then the result will
        be a two-element list where the first element is a numpy array for
        the I coordinates and the second element is a numpy array for
        the J coordinates.

    Examples:
        print(nsidc_polar_lonlat(350.0, 34.41, 12.5, 1))
            [608, 896]
    """
    import numpy as np
    
    _validate_grid_size(grid_size)
    hemisphere = _validate_hemisphere(hemisphere)

    delta, imax, jmax, xmin, ymin = _grid_params(grid_size, hemisphere)

    x, y = _polar_lonlat_to_xy(
        longitude + delta,
        np.abs(latitude),
        TRUE_SCALE_LATITUDE,
        EARTH_RADIUS_KM,
        EARTH_ECCENTRICITY,
        hemisphere
    )
    
    # removed `+ 1` in original code that made the indices 1-based
    i = (np.round((x - xmin) / grid_size)).astype(int)
    j = (np.round((y - ymin) / grid_size)).astype(int)
    # Flip grid_size orientation in the 'y' direction
    j = (jmax - 1) - j
    
    return [i, j]


#=========================
# Standard error messaging
#=========================

def error_msg(msg):
    """
    Print an error message with a warning icon and exit the program.

    Parameters
    ----------
    msg : str
        The error message to display in the console.

    Notes
    -----
    - This function immediately terminates the program using `exit()`.
    """

    
    print(f"  ⚠️ {msg}")
    exit()
    
    
#===================
# Internal functions
#===================

def _set_transformer(epsg=3411):
    transformer = {}
    
    # CRS setup
    transformer['epsg'] = epsg
    transformer['crs_string_3413'] = CRS.from_string(
        "+proj=stere +lat_0=90 +lat_ts=70 +lon_0=-45 "
        "+x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs +type=crs"
    )
    transformer['crs_string_4326'] = CRS.from_string(
        "+proj=longlat +datum=WGS84 +no_defs +type=crs"
    )
    transformer["crs_string_3408"] = CRS.from_string(
        "+proj=laea +lat_0=90 +lon_0=0 "
        "+x_0=0 +y_0=0 "
        "+a=6371228 +b=6371228 "
        "+units=m +no_defs +type=crs"
    )
    
    transformer["crs_string_3411"] = CRS.from_string(
        "+proj=stere +lat_0=90 +lat_ts=70 +lon_0=-45 "
        "+x_0=0 +y_0=0 +a=6378273 +b=6356889.449 "
        "+units=m +no_defs +type=crs"
    )
    
    transformer['proj4_3413_dict'] = {
        "proj": "stere",
        "lat_0": 90,
        "lat_ts": 70,
        "lon_0": -45,
        "x_0": 0,
        "y_0": 0,
        "datum": "WGS84",
        "units": "m",
        "no_defs": True
    }
    
    transformer['4326_to_3413'] = Transformer.from_crs(
        transformer['crs_string_4326'],
        transformer['crs_string_3413'],
        always_xy=True
    )

    transformer['3413_to_4326'] = Transformer.from_crs(
        transformer['crs_string_3413'],
        transformer['crs_string_4326'],
        always_xy=True
    )
    
    transformer['4326_to_3408'] = Transformer.from_crs(
        transformer['crs_string_4326'],
        transformer['crs_string_3408'],
        always_xy=True
    )
    
    transformer['4326_to_3411'] = Transformer.from_crs(
        transformer['crs_string_4326'],
        transformer['crs_string_3411'],
        always_xy=True
    )
    
    return transformer


def _set_metadata(config):
    """
    Generate a NetCDF metadata template using a CDL file and load
    it as an xarray.Dataset.
    
    This function takes the user-defined CDL (Common Data Language)
    file path from the `user_args` dictionary, runs the `ncgen` 
    command-line tool to convert it into a NetCDF (.nc) file,
    and then loads that file into memory using `xarray`.
    
    The function is typically used to extract metadata
    (attributes and structure) from a CDL file so that it can be applied
    to a data-driven NetCDF file.
    
    Parameters:
        user_args (dict): Dictionary containing user-provided arguments,
        including:
            - 'metadata_dir' (str): Path to the directory where CDL file
                                    is stored.
    
    Returns:
        xarray.Dataset: A dataset containing only metadata
                        from the generated NetCDF file.
    
    Raises:
        SystemExit: If the `ncgen` command fails or
                    returns a non-zero status code.
    """
    
    # COnfirm naming convention meets standards


    import os
    import subprocess
    import xarray as xr
    
    cdl_file = config['netcdf_cdl_file']
    cdl_file_dir = os.path.dirname(cdl_file)
    cdl_file_basename = os.path.basename(cdl_file)
    # Prepare ncgen input and output filenames

    
    ncgen_ofile_nc = os.path.join(
        cdl_file_dir, f"{cdl_file_basename}.nc"
        )
    
    
    # Run ncgen command to generate the netCDF file from CDL
    myCmd1 = " ".join(
        [
            "ncgen",
            "-o",
            ncgen_ofile_nc,
            cdl_file,
        ]
    )
        
    rc = subprocess.call(myCmd1, shell=True)
    if rc != 0:
        error_msg(
            'Error in `ncgen` call. Cannot continue.\n'
            f'Command: {myCmd1}\nError Code: {rc}', 
            25
        )
        
    return xr.open_dataset(ncgen_ofile_nc, decode_times=False)


def _read_geotiff_rasterio(geotiff_file):
    """
    Reads a GeoTIFF image using GCP-based reprojection to EPSG:3413
    (NSIDC Sea Ice Polar Stereographic North) and returns a masked
    array with coordinate information.
    
    This function:
        - Opens a GeoTIFF file using rasterio
        - Extracts Ground Control Points (GCPs) to reproject the image
        to a target CRS (EPSG:3413)
        - Uses nearest-neighbor resampling to regrid the data
        - Constructs an xarray.DataArray with spatial coordinates in meters
        - Masks background values (zeros) to allow clean visualization
        - Computes the image extent for use in plotting (e.g., with imshow)
    
    Parameters:
        geotiff_path (str): Path to the input GeoTIFF file containing
                            GCPs and raster data.
    
    Returns:
        tuple:
            masked_xr (np.ma.MaskedArray): Masked 2D array of image data
                                           with background set to NaN.
            extent (list): [xmin, xmax, ymin, ymax] extent of the image
                           in meters (EPSG:3413) for use with plotting.
    Coauthor:
        Rachael Lazzaro, rachel.lazzaro@noaa.gov
    """
    
    
    import rasterio
    from rasterio.warp import reproject, Resampling
    from rasterio.warp import calculate_default_transform
    import xarray as xr
    import numpy as np
   

    with rasterio.open(geotiff_file) as src:
        gcps, gcps_crs = src.get_gcps()
        dst_crs = "EPSG:3413"
        dst_transform, width, height = calculate_default_transform(
            gcps_crs, dst_crs, src.width, src.height, gcps=gcps
        )

        dst_array = np.empty(
            (src.count, height, width), 
            dtype=src.dtypes[0]
        )

        reproject(
            source=rasterio.band(src, 1),
            destination=dst_array[0],
            src_crs=gcps_crs,
            src_transform=None, # None triggers GCP-based warping
            gcps=gcps,          # Let rasterio warp based on GCPs
            dst_transform=dst_transform,
            dst_crs=dst_crs,
            resampling=Resampling.nearest
        )
        
        # Construct xarray.DataArray with coordinates
        x_coords = dst_transform[2] + dst_transform[0] * np.arange(width)
        y_coords = dst_transform[5] + dst_transform[4] * np.arange(height)
        
        geotiff_xr = xr.DataArray(
            dst_array[0],
            dims=("y", "x"),
            coords={"x": x_coords, "y": y_coords},
            attrs={"crs": dst_crs}
        )
        
        # change backround to white
        masked_xr = np.ma.masked_equal(geotiff_xr.values, 0)
        
        extent = [
            dst_transform[2],
            dst_transform[2] + dst_transform[0] * width,
            dst_transform[5] + dst_transform[4] * height,
            dst_transform[5],
        ]
        
        return masked_xr, extent
        

def _embed_qml_style(gpkg_path, layer_name, qml_path):
    """
    Embed a QML style into a GeoPackage's layer_styles table.

    Reads a QML file and writes its contents into the QGIS-standard
    layer_styles table inside the GeoPackage. QGIS will automatically
    apply the style when the layer is loaded, requiring no QML file
    on the end user's machine.

    Args:
        gpkg_path (str): Full path to the target GeoPackage file.
        layer_name (str): Name of the layer to apply the style to.
                          Must match the layer name in the GeoPackage exactly.
        qml_path (str): Full path to the QML style file to embed.

    Returns:
        None

    Notes:
        - The layer_styles table is created if it does not already exist,
          following the QGIS standard schema.
        - `f_geometry_column` is hardcoded to 'geom' because GeoPandas
          silently renames the geometry column from 'geometry' to 'geom'
          when writing to GeoPackage format.
        - `useAsDefault` is set to 1 so QGIS applies the style automatically
          on load without user intervention.
        - The layer_styles table is registered in gpkg_contents as an
          attributes layer for full GeoPackage spec compliance.
    """
    import sqlite3
    
    with open(qml_path, 'r') as f:
        qml_content = f.read()

    conn = sqlite3.connect(gpkg_path)
    cursor = conn.cursor()

    # Create layer_styles table if it doesn't exist (QGIS standard schema)
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS layer_styles (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       f_table_catalog TEXT,
                       f_table_schema TEXT,
                       f_table_name TEXT,
                       f_geometry_column TEXT,
                       styleName TEXT,
                       styleQML TEXT,
                       styleSLD TEXT,
                       useAsDefault INTEGER,
                       description TEXT,
                       owner TEXT,
                       ui TEXT,
                       update_time DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """
    )


    cursor.execute("""
                   INSERT INTO layer_styles 
                   (f_table_catalog, f_table_schema, f_table_name, 
                    f_geometry_column, styleName, styleQML, styleSLD,
                    useAsDefault, description, owner)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                   """,
                   (
                       '',           # f_table_catalog
                       '',           # f_table_schema
                       layer_name,   # f_table_name  
                       'geom',       # f_geometry_column
                       'outliers',   # styleName
                       qml_content,  # styleQML
                       '',           # styleSLD (leave blank)
                       1,            # useAsDefault
                       '',
                       ''
                    )
    )
    
    cursor.execute("""
                   INSERT OR IGNORE INTO gpkg_contents 
                   (table_name, data_type, identifier, description,
                    last_change)
                   VALUES 
                   ('layer_styles', 'attributes', 'layer_styles',
                    'QGIS layer styles', datetime('now'))
                   """
    )

    conn.commit()    
    conn.close()


#=============
# Calculations
#=============

def _circular_mean(a):
    import numpy as np
    return np.arctan2(np.nanmean(np.sin(a)), np.nanmean(np.cos(a)))


def _circular_std(a):
    import numpy as np
    s = np.nanmean(np.sin(a))
    c = np.nanmean(np.cos(a))
    R = np.sqrt(s*s + c*c)
    return np.sqrt(-2 * np.log(np.clip(R, 1e-12, 1.0)))


#==================
# Plot enhancements
#==================

def _add_graticules(ax, map_extent):
    """
    Add latitude and longitude graticules with labels to a Cartopy map axis.
    
    This function draws dashed gridlines (graticules) at regular intervals
    of longitude and latitude on a projected plot using EPSG:3413
    (NSIDC Sea Ice Polar Stereographic North). Longitude labels are placed
    near the bottom of the plot and labeled in degrees west. Latitude labels
    are placed along the right edge in degrees north.
    
    Parameters
    ----------
    ax : matplotlib.axes._subplots.AxesSubplot
        A Cartopy-projected Matplotlib axis to which graticules will be added.
    
    map_extent_xr : list of float
        The extent of the plotted map in EPSG:3413 projected coordinates, 
        given as [xmin, xmax, ymin, ymax].
    
    Notes
    -----
    - Graticules are drawn every 10 degrees longitude and 
      every 5 degrees latitude.
    - The function internally transforms coordinates using `pyproj`
      for EPSG:3413 <-> EPSG:4326.
    - A 10% buffer is added to both longitude and latitude ranges to ensure
      full graticule coverage.
    - Labels are drawn in projected space (not geographic space).
    - Longitude labels use west notation (e.g., 135°W),
      and latitude uses north (e.g., 75.0°N).
    """
    
    
    import numpy as np
    
    # Corners in degrees transform from EPSG:3413 to EPSG:4326
    transformer = _set_transformer()
    lon_min, lat_min = (
        transformer['3413_to_4326'].transform(map_extent[0], map_extent[2])
    )
    lon_max, lat_max = (
        transformer['3413_to_4326'].transform(map_extent[1], map_extent[3])
    )
    
    # Fix inverted bounds
    lon_min, lon_max = sorted([lon_min, lon_max])
    lat_min, lat_max = sorted([lat_min, lat_max])
   
    
    # Generate labels (every 5 degrees lat; every 10 degrees lon)
    # Only include multiples of 5 within the actual bounds
    lon_labels = np.arange(
        np.ceil(lon_min / 10) * 10,
        np.floor(lon_max / 10) * 10 + 1,
        10
    )
    
    lat_labels = np.arange(
        np.ceil(lat_min / 5) * 5,
        np.floor(lat_max / 5) * 5 + 1,
        5
    )

    
    # Extend the longitude/latitude range slightly (e.g., 10%) 
    # to ensure full coverage
    lon_range = lon_max - lon_min
    lon_pad = 0.1 * lon_range  # 10% padding
    lon_min_ext = lon_min - lon_pad
    lon_max_ext = lon_max + lon_pad
    
    lat_range = lat_max - lat_min
    lat_pad = 0.1 * lat_range
    lat_min_ext = lat_min - lat_pad
    lat_max_ext = lat_max + lat_pad
    
    
    # Vertical lines for longitude
    for lon in lon_labels:
        lats = np.linspace(lat_min_ext, lat_max_ext, 200)
        points = []
        for lat in lats:
            points.append(transformer['4326_to_3413'].transform(lon, lat))
        xs, ys = zip(*points)
        ax.plot(xs, ys, color='lightgray', linestyle='--', linewidth=0.5)
        
    # longitude labels
    for lon in lon_labels:
        x, y = transformer['3413_to_4326'].transform(lon, lat_min)
        ax.text(
            x + 30000,
            y + 5000,
            f"{lon:.0f}°W",
            ha='center',
            va='top',
            fontsize=8
        )


    # horizontal lines for latitude    
    for lat in lat_labels:
        lons = np.linspace(lon_min_ext, lon_max_ext, 200)
        points = []
        for lon in lons:
            points.append(transformer['4326_to_34123'].transform(lon, lat))
        xs, ys = zip(*points)
        ax.plot(xs, ys, color='lightgray', linestyle='--', linewidth=0.5)    
    
    # Label latitudes at right
    for lat in lat_labels:
        x, y = transformer['4326_to_3413'].transform(lon_labels[-1], lat)
        ax.text(
            x - 5000,
            y - 10000,
            f"{lat:.1f}°N",
            ha='left',
            va='center',
            fontsize=8
        )


def _add_scale(ax, cartopy_crs):
    """
    Add a scale bar to a Cartopy-projected map axis.
    
    This function uses the `matplotlib_scalebar` library to draw a scale bar
    that indicates real-world distance in kilometers. It assumes the map
    projection uses meters as its base unit (e.g., EPSG:3413).
    
    Parameters
    ----------
    ax : matplotlib.axes._subplots.AxesSubplot
        A Matplotlib axis with a Cartopy projection to which the scale bar
        will be added.
    
    cartopy_crs : cartopy.crs.Projection
        The projection used for the map, assumed to be in meters. Although not
        directly used, this parameter is kept for compatibility and clarity.
    
    Notes
    -----
    - The scale bar spans 25% of the axis width.
    - The bar displays a fixed length of 100 kilometers.
    - The position of the scale bar is anchored to the lower left corner
      of the plot.
    - The axis is assumed to use projected units in meters
      (e.g., Polar Stereographic).
    """
    
    
    from matplotlib_scalebar.scalebar import ScaleBar
    
    # Add scalebar to ax
    scalebar = ScaleBar(
        dx=1,                  # 1 data unit = 1 meter
        units='m',             # tell it the CRS uses meters
        location='lower left',
        scale_loc='bottom',
        length_fraction=0.25,  # bar spans 25% of axis
        fixed_value=100,       # (optional) force bar to 100 km
        fixed_units='km'       # force label to km
    )
    ax.add_artist(scalebar)
    
    
def _add_true_north(ax, xmin, xmax, ymin, ymax):
    """
    Add a True North arrow to a Cartopy map axis using EPSG:3413 coordinates.

    This function adds an arrow pointing to geographic North at a reference
    location near the bottom-right corner of the plot. The location is computed
    in the EPSG:3413 projection (Polar Stereographic North), and then
    converted to geographic coordinates (EPSG:4326) to calculate the northward
    direction.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The Matplotlib axis on which to draw the True North arrow.

    xmin : float
        Minimum x-coordinate (in meters) of the map extent.

    xmax : float
        Maximum x-coordinate (in meters) of the map extent.

    ymin : float
        Minimum y-coordinate (in meters) of the map extent.

    ymax : float
        Maximum y-coordinate (in meters) of the map extent.

    Notes
    -----
    - The north arrow is drawn at 5% from the right and 5% from the bottom
      of the map.
    - The arrow is styled with a black face and labeled with an 'N'
      to indicate direction.
    - Coordinate conversions between EPSG:3413 and EPSG:4326 are performed
      using `pyproj.Transformer`.
    """
    
    
    
    transformer = _set_transformer()
    
    # bottom-right corner of the plot as reference point
    x_ref = xmax - 0.05 * (xmax - xmin)
    y_ref = ymin + 0.05 * (ymax - ymin)
    
    # convert meters to degrees
    lon_ref, lat_ref = transformer['3413_to_4326'].transform(x_ref, y_ref)
    
    # move a small distance north
    lat_north = lat_ref + 0.5
    lon_north = lon_ref
    
    # convert degrees back to meters
    x_north, y_north = transformer['4326_to_3413'].transform(lon_north, lat_north)
    
    # arrow
    ax.annotate(
        '', xy=(x_north, y_north), xytext=(x_ref, y_ref),
        arrowprops=dict(
            facecolor='black', edgecolor='black', width=2, headwidth=10
        ),
    )
    ax.text(
        x_ref, y_ref - 20000, 'N', color='black',
        fontsize=16, ha='center', va='top'
    )
    
    
#=========
# Data I/O
#=========

def read_sar_drift_data_file(input_file, config, skip_rows=None):
    """
    Read and preprocess a SAR ice-drift text data file into a standardized
    DataFrame.

    This function loads a SAR drift data file (CSV-like text) using parsing
    rules provided in `config`, cleans column names, removes known-bad
    observations, and derives additional time, duration, unit-converted
    velocity, and satellite fields.

    Processing steps:
        - Read the file with `pandas.read_csv()` using delimiter and
          header offsets from `config`.
        - Strip whitespace from column names.
        - Remove rows where `Bear_deg == 0` (known invalid bearings/records).
        - Normalize longitudes from 0–360 to -180/180 range for
          `Lon1` and `Lon2`.
        - Convert SAR "Julian seconds" timestamps (seconds since 2000-01-01)
          in `Time1_JS` and `Time2_JS` to human-readable `Date1` and `Date2`.
        - Compute duration between start and end times in both timedelta
          string form (`Duration`) and raw seconds (`JS_Duration`).
        - Convert speed from km/day to m s⁻¹:
            - `Speed_kmdy` -> `Speed_ms`
        - Extract satellite identifiers from `File1` and `File2`
          into `Sat1` and `Sat2`.

    Args:
        input_file (str or pathlib.Path): Path to the SAR drift data file
                                          to read.
        config (dict): Parsing configuration. Expected keys:
            - 'delimiter' (str): Field delimiter passed to `pd.read_csv`.
            - 'skip_rows_before_header' (int): Number of rows to skip before
              the header row.

    Returns:
        pandas.DataFrame: Cleaned and enriched SAR drift DataFrame containing
        original fields plus derived columns including:
            - 'Date1', 'Date2' (str): Start/end timestamps in
                                      '%Y-%m-%d %H:%M:%S'.
            - 'Duration' (str): Duration as a timedelta string.
            - 'JS_Duration' (numeric): Duration in seconds
                                       (Time2_JS - Time1_JS).
            - 'Speed_ms' (float): Speed converted from km/day to m s⁻¹.
            - 'Sat1', 'Sat2' (str): Satellite identifiers extracted
                                    from File1/File2.

    Notes:
        - SAR time fields `Time1_JS` and `Time2_JS` are interpreted as
          seconds since 2000-01-01 00:00:00.
        - Longitudes are normalized from 0–360 to -180/180 to ensure
          correct rendering in QGIS and compatibility with downstream
          projections.
        - A specific `pyproj` warning about database path setup is suppressed
          because it is expected in this runtime environment.
        - This function assumes the input file includes the required columns:
          'Bear_deg', 'Time1_JS', 'Time2_JS', 'U_vel_ms', 'V_vel_ms',
          'Speed_kmdy', 'File1', and 'File2'.
    """
    
    import pandas as pd
    from datetime import datetime, timedelta
    
    # The project database for pyproj is properly set by the code above
    # Okay to ignore this warning and only this warning
    import warnings
    warnings.filterwarnings(
        "ignore",
        category=UserWarning,
        module="pyproj",
        message="pyproj unable to set database path"
    )
    
    
    # Read the SAR drift data file
    df = pd.read_csv(
        input_file, delimiter=config['delimiter'],
        header=0, engine='c', skiprows=skip_rows
    )
    df.columns = df.columns.str.strip()
    
    
    # Add the appropriate input file to a data frame
    # Julian seconds start from date 01-01-2000
    base_time = datetime(2000, 1, 1)

    # Create new Date* columnc by converting Time_JS* columns to datetime
    df['Date1'] = df["Time1_JS"].apply(
        lambda x: base_time + timedelta(seconds=x)
        )
    df['Date1'] = df['Date1'].dt.strftime('%Y-%m-%d %H:%M:%S')
    df['Date2'] = df["Time2_JS"].apply(
        lambda x: base_time + timedelta(seconds=x)
        )
    df['Date2'] = df['Date2'].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    
    # need to mormalize longitudes since the file was created in
    # Polar stereogrpahic despite having lon/lat
    # This transitions helps future projections and if files opened in QGIS
    df['Lon1'] = df['Lon1'].apply(lambda x: x - 360 if x > 180 else x)
    df['Lon2'] = df['Lon2'].apply(lambda x: x - 360 if x > 180 else x)


    # Calculate duration of observations
    # 1. Date time
    # 2. Raw Julian seconds
    df['Duration'] = pd.to_timedelta(
        df['Time2_JS'] - df['Time1_JS'], unit='s'
        ).astype(str)
    df['JS_Duration'] = (
        df['Time2_JS'] - df['Time1_JS']
        )
    
    
    # convert speed units to m/s-1
    SECONDS_PER_DAY = 86400.0
    df['Speed_ms'] = (df['Speed_kmdy'] * 1000) / SECONDS_PER_DAY
    
    
    # identify satellites for analysis
    df['Sat1'] = df["File1"].str.partition("_")[0]
    df['Sat2'] = df["File2"].str.partition("_")[0]


    return df


def outlier_search(df, config, base_name, radius_km,
                   min_neighbors, md_neighbors, z_score_level,
                   chi_square_level, passes):
    import numpy as np
    import logging
    from scipy.spatial import cKDTree
    from sklearn.covariance import MinCovDet, LedoitWolf
    from scipy.stats import chi2
    
    if config['version'] == '01':
        # no outlier deteection required
        df['outlier_category'] = '-9'
        return df
    

    out_df = df.reset_index(drop=True).copy()
    
    radius_m = radius_km * 1000
    iter_prev_inliers = None
    quiver_payloads_by_iter = []
    
    # create scene groupings based on `File` and `File2` values
    out_df = out_df.sort_values(by=['File1', 'File2'], ascending=True)
    out_df = out_df.reset_index(drop=True) # reset index after sorting
    out_df["bearing_rad"] = np.deg2rad(out_df["Bear_deg"].to_numpy())
    out_df["outlier_category"] = '01' # default value of significant inlier
    out_df["sd_neighbor_indices"] = None
    out_df["sd_neighbor_count"] = 0
    out_df["distance_z_score"] = np.nan
    out_df["bearing_z_score"] = np.nan
    out_df['md_neighbor_indices'] = None
    out_df['md_neighbor_count'] = 0
    out_df['mahal_sq'] = np.nan
    out_df['thr_sq'] = np.nan
    out_df['mahal_outlier_flag'] = False
    out_df['sd_outlier_pass'] = -1
    out_df['md_outlier_pass'] = -1
    
    # for the neighbor search to work, the projection needs
    # to be changed to EPSG:3411
    tf = _set_transformer(3411)
    out_df['X1'], out_df['Y1'] = tf['4326_to_3411'].transform(
        out_df['Lon1'].to_numpy(),
        out_df['Lat1'].to_numpy(),
    )
    
    # create scene index for each File1, File2 pairing
    out_df["scene"] = out_df.groupby(
        ['File1', 'File2'],
        sort=False
    ).ngroup() + 1
   

    # iterate passes through data to identify outliers and recheck
    # recommended to leave just two passes so data don't get too homogenized
    for pass_idx in range(passes):
        # iteratively run outlier detection until no new outliers found
        # instantiate pool data frame
        # keep any inlier whether confident or not
        pool_df = out_df[out_df['outlier_category'].isin(['00', '01'])].copy() 
        inlier_count = (out_df['outlier_category'] == '01').sum()
        
        
        quiver_payloads_by_iter.append({
            'LON': pool_df['Lon1'].to_numpy(),
            'LAT': pool_df['Lat1'].to_numpy(),
            'U': pool_df['U_vel_ms'].to_numpy(),
            'V': pool_df['V_vel_ms'].to_numpy()
        })
        
        # stop if stable
        if iter_prev_inliers is not None and \
            inlier_count == iter_prev_inliers:
                break
        iter_prev_inliers = inlier_count

        
        # create neighbors for each scene            
        for scene_id, scene_df in pool_df.groupby("scene", sort=False):
            xy = scene_df[["X1", "Y1"]].to_numpy()
            
            if len(xy) == 0:
                continue
            
            tree = cKDTree(xy)
            all_neighbors = tree.query_ball_point(xy, r=radius_m)
            Xall = scene_df[['U_vel_ms', 'V_vel_ms']].to_numpy()

            
            for local_idx, local_neighbors in enumerate(all_neighbors):
                
                # drop self
                neigh_idxs = [
                    j for j in local_neighbors if j != local_idx
                ]
                
                target_out_idx = scene_df.index[local_idx]
                
                if len(neigh_idxs) == 0:
                    continue
                
                neigh_rows = scene_df.iloc[neigh_idxs]

                neigh_dist = neigh_rows['Speed_ms'].to_numpy()
                neigh_bear = neigh_rows['bearing_rad'].to_numpy()
                
                
                # compute neighbor mean and standard deviation
                dist_mean = np.nanmean(neigh_dist)
                dist_std = np.nanstd(neigh_dist)
                bear_mean = _circular_mean(neigh_bear)
                bear_std = _circular_std(neigh_bear)
                
                # get current cell values
                cell_dist = scene_df.iloc[local_idx]["Speed_ms"]
                cell_bear = scene_df.iloc[local_idx]["bearing_rad"]
                
                # compute z-score absolute value makes it two-sided
                if (dist_std == 0) or np.isnan(dist_std):
                    dist_z_score = np.nan
                else:   
                    dist_z_score = (np.abs(cell_dist - dist_mean)/dist_std)
                # dist_z_scores.append(dist_z_score)
                # normalize the radians because mean = 359° and cell = 1°
                # subtraction gives 358°, but the real smallest difference
                # is 2°. Use delta as a measurement of standard deviation
                delta_bear = np.arctan2(
                    np.sin(cell_bear - bear_mean),
                    np.cos(cell_bear - bear_mean)
                )
                if (bear_std == 0) or np.isnan(bear_std):
                    bear_z_score = np.nan
                else:
                    bear_z_score = np.abs(delta_bear) / bear_std

                
                # store neighbors as out_df indices
                neigh_out_idx = [
                    int(scene_df.index[j]) for j in neigh_idxs
                ]
                neigh_out_idx = [
                    i for i in neigh_out_idx if i != target_out_idx
                ]
    
                
                out_df.at[target_out_idx, "sd_neighbor_indices"] = (
                    neigh_out_idx
                )
                out_df.at[target_out_idx, "sd_neighbor_count"] = (
                    len(neigh_out_idx)
                )
                out_df.at[target_out_idx, "distance_z_score"] = (
                    np.round(dist_z_score, 3)
                )
                out_df.at[target_out_idx, "bearing_z_score"] = (
                    np.round(bear_z_score, 3)
                )
                

                # Mahalanobis distance
                k_md = min(md_neighbors+1, len(scene_df))
                distances, all_neighbors = tree.query(xy, k=k_md)
                neigh_idxs = all_neighbors[local_idx].tolist()
                # drop self
                neigh_idxs  = [j for j in neigh_idxs if j != local_idx] 
                
            
                # Mahalanobis on neighbors
                x = Xall[local_idx, :] # target vector
                Xn = Xall[neigh_idxs, :] # neighbor matrix
                
                # Need enough neighbors to estimate covariance robustly
                p = Xn.shape[1] # degrees of freedom
                if len(neigh_idxs) < max(2 * p + 1, md_neighbors) or \
                    k_md < md_neighbors + 1:
                    mahal_sq = np.nan
                else:
                    # standardize data
                    mu = Xn.mean(axis=0)
                    sd = Xn.std(axis=0)
                    sd[sd == 0] = 1.0
                    Xn_z = (Xn - mu) / sd
                    x_z = (x - mu) / sd
                    
                    if np.linalg.matrix_rank(Xn_z) < p:
                        mahal_sq = np.nan
                    else:
                        # standard covariance measurement
                        # mcd = MinCovDet().fit(Xn_z)
                        # squared distance
                        # mahal_sq = mcd.mahalanobis([x_z])[0]
                        # better for small  samples or the covariance
                        # is ill-conditioned.
                        lw = LedoitWolf().fit(Xn_z) 
                        mahal_sq = lw.mahalanobis([x_z])[0] # squared distance
                    
                    
                alpha = chi_square_level # 99 strict threshold
                thr_sq = chi2.ppf(alpha, df=p)  # squared-distance threshold
                
                # store neighbors as out_df indices
                neigh_out_idx = [
                    int(scene_df.index[j]) for j in neigh_idxs
                ]
                neigh_out_idx = [
                    i for i in neigh_out_idx if i != target_out_idx
                ]
                
                
                out_df.at[target_out_idx, "md_neighbor_indices"] = (
                    neigh_out_idx
                )
                out_df.at[target_out_idx, "md_neighbor_count"] = (
                    len(neigh_out_idx)
                )
                out_df.at[target_out_idx, 'mahal_sq'] = mahal_sq
                out_df.at[target_out_idx, 'thr_sq'] = thr_sq
                out_df.at[target_out_idx, 'mahal_outlier_flag'] = (
                    (mahal_sq > thr_sq)
                )
                
                
            ### TEST ON FULL SENE (index to right when done)
            # # 1) Build full-scene feature matrix
            # Xall = out_df[["U_vel_ms", "V_vel_ms"]].to_numpy(dtype=float)
            # n, p = Xall.shape
            
            # # Optional: drop rows with non-finite values (recommended)
            # finite_mask = np.isfinite(Xall).all(axis=1)
            
            # # Initialize outputs (so you can keep original length)
            # mahal_sq = np.full(n, np.nan, dtype=float)
            
            # if finite_mask.sum() >= max(2 * p + 1, md_neighbors):   # keep your minimum sample rule
            #     X = Xall[finite_mask]
            
            #     # 2) Standardize using full-scene stats
            #     mu = X.mean(axis=0)
            #     sd = X.std(axis=0, ddof=0)
            #     sd[sd == 0] = 1.0
            #     Xz = (X - mu) / sd
            
            #     # 3) Fit covariance once (scene-wide)
            #     lw = LedoitWolf().fit(Xz)
            
            #     # 4) Mahalanobis squared distances for all points (scene-wide)
            #     mahal_sq[finite_mask] = lw.mahalanobis(Xz)  # returns squared distances
            
            # # 5) Threshold (chi-square, df=p)
            # alpha = chi_sq
            # thr_sq = float(chi2.ppf(alpha, df=p))
            
            # # 6) Store results
            # out_df["mahal_sq"] = mahal_sq
            # out_df["thr_sq"] = thr_sq
            # out_df["mahal_outlier_flag"] = (out_df["mahal_sq"] > out_df["thr_sq"]).fillna(False)
            
            # # 7) Neighbor fields no longer mean "neighbors"—repurpose or simplify
            # # If you want "count used for scene covariance":
            # out_df["md_neighbor_count"] = int(finite_mask.sum()) - 1  # "others in scene" (approx)
            # # If you don't want indices, keep empty lists or None:
            # out_df["md_neighbor_indices"] = None
            # md_neighbors = int(finite_mask.sum()) - 1                 

                
                
            """
            assign outlier category
            00: None (under neighbor threshold)
            01: None (equal to or above neighbor threshold)
            10: Distance (under neighbor threshold)
            11: Distance (equal to or above neighbor threshold)
            20: Bearing (under neighbor threshold)
            21: Bearing (equal to or above neighbor threshold)
            30: Mahalanobis distance (under neighbor threshold)
            31: Mahalanobis distance (equal to or above neighbor threshold)
            40: Distance and bearing (under neighbor threshold)
            41: Distance and bearing (equal to or above neighbor threshold)
            50: Mahalanobis distance and distance (under neighbor threshold)
            51: Mahalanobis distance and distance
                (equal to or above neighbor threshold)
            60: Mahalanobis distance and bearing (under neighbor threshold)
            61: Mahalanobis distance and bearing
                (equal to or above neighbor threshold)            
            70: Mahalanobis distance, distance and bearing
                (under neighbor threshold)
            71: Mahalanobis distance, distance and bearing
                (equal to or above neighbor threshold)
            """
            
            # outlier boolean flags
            distance_filter = out_df['distance_z_score'] > z_score_level
            bearing_filter = out_df['bearing_z_score'] > z_score_level
            md_filter = out_df["mahal_outlier_flag"].astype(bool)
            
            # set confidence
            sd_statistical_confidence_flag = (
                out_df["sd_neighbor_count"] >= min_neighbors
            ).astype(np.int8) # force 0/1 not True/False
    
            md_statistical_confidence_flag = (
                out_df["md_neighbor_count"] >= md_neighbors
            ).astype(np.int8) # force 0/1 not True/False
            
            
            # base category set to all zeros
            base_cat = np.zeros(len(out_df), dtype=np.int8)
            
            # order matters
            mask_md_d_b = md_filter & distance_filter & bearing_filter
            mask_md_d   = md_filter & distance_filter & ~bearing_filter
            mask_md_b   = md_filter & ~distance_filter & bearing_filter
            mask_md     = md_filter & ~distance_filter & ~bearing_filter            
            mask_d_b    = ~md_filter & distance_filter & bearing_filter
            mask_d      = ~md_filter & distance_filter & ~bearing_filter
            mask_b      = ~md_filter & ~distance_filter & bearing_filter
            
            base_cat[mask_md_d_b] = 7
            base_cat[mask_md_b]   = 6
            base_cat[mask_md_d]   = 5
            base_cat[mask_d_b]    = 4
            base_cat[mask_md]     = 3            
            base_cat[mask_b]      = 2
            base_cat[mask_d]      = 1
    
            # complete statistical confidence flag
            # use MD confidence whenever MD is involved;
            # otherwise SD confidence
            md_involved = np.isin(base_cat, [3, 5, 6, 7])
            statistical_confidence_flag = np.where(
                md_involved, # was Mahalanobis filter used
                md_statistical_confidence_flag, # true
                sd_statistical_confidence_flag # false
            ).astype(np.int8)
            
            
            # record which pass
            sd_outlier_now = (distance_filter | bearing_filter)
            md_outlier_now = md_filter
            out_df.loc[
                sd_outlier_now & (
                    out_df["sd_outlier_pass"] == -1
                ), "sd_outlier_pass"] = pass_idx + 1
            out_df.loc[md_outlier_now & (
                out_df["md_outlier_pass"] == -1
                ), "md_outlier_pass"] = pass_idx + 1
            
            # update data frame
            out_df["outlier_category"] = (
                base_cat.astype(str) + statistical_confidence_flag.astype(str)
            )
            
            # log outlier counts per pass
            total = len(out_df)
            n_inliers = int((base_cat == 0).sum())
            n_distance = int(mask_d.sum())
            n_bearing = int(mask_b.sum())
            n_md = int(mask_md.sum())
            n_d_b = int(mask_d_b.sum())
            n_md_d = int(mask_md_d.sum())
            n_md_b = int(mask_md_b.sum())
            n_md_d_b = int(mask_md_d_b.sum())
            n_outliers = total - n_inliers
            
            logger = logging.getLogger('sar_drift')
            logger.info(
                f"Scene {base_name} | Pass {pass_idx + 1} | "
                f"total={total} | inliers={n_inliers} | outliers={n_outliers} | "
                f"distance={n_distance} | bearing={n_bearing} | "
                f"mahalanobis={n_md} | dist+bear={n_d_b} | "
                f"md+dist={n_md_d} | md+bear={n_md_b} | "
                f"md+dist+bear={n_md_d_b}"
            )


        ### TEST CASE 0782302767 ####
        
    
    return out_df


def create_netcdf(df, base_name, config, template_ds, scene_i_j):
    """
    Create a gridded NetCDF sea-ice drift product from point/vector
    observations.

    This function maps input drift vectors (lon/lat locations with speed and
    displacement components) onto a polar stereographic grid, populates a
    NetCDF dataset using attributes from a metadata/template dataset, crops
    the output to the spatial extent of valid observations (with padding),
    and writes the result to disk with compression.

    Args:
        df (pandas.DataFrame): Input table of drift observations.
        Expected columns:
            - 'Date1' (datetime-like): Start timestamp for the vector.
            - 'Date2' (datetime-like): End timestamp for the vector.
            - 'Lon1' (float): Starting longitude (degrees).
            - 'Lat1' (float): Starting latitude (degrees).
            - 'Speed_ms' (float): Sea-ice speed (m s-1).
            - 'U_vel_ms' (float): X displacement component (m s-1).
            - 'V_vel_ms' (float): Y displacement component (m s-1).
            - 'Bear_deg' (float): Direction of sea-ice displacement (degrees).
        base_name (str): Base filename (without extension) used to name
                         the output NetCDF file
                         `<config['nc_dir']>/<base_name>.nc`.
        config (dict): Configuration dictionary. Must include:
            - 'nc_dir' (str): Output directory where the NetCDF file
                              is written. Also used by `_set_metadata(config)`
                              to populate global/variable attributes.
        template_ds (xarray.Dataset): Template dataset providing the
                                      target grid coordinate arrays and
                                      dimensions.
    Returns:
        None


    Workflow:
        1. Normalize input timestamps (`Date1`, `Date2`) to pandas datetimes.
        2. Convert starting lon/lat positions (`Lon1`, `Lat1`) to grid
           indices (i, j) using `_polar_lonlat_to_ij(...)`.
        3. Build an output dataset using variable/global attributes
           from `_set_metadata(config)` while using the coordinate arrays
           from `template_ds`.
        4. Populate the first (and only) time slice with the vector fields:
           - sea_ice_speed
           - sea_ice_x_displacement
           - sea_ice_y_displacement
           - direction_of_sea_ice_displacement
        5. Crop the dataset to the bounding box of valid observations
           with padding.
        6. Write the dataset to NetCDF using zlib compression (level 4).

    Notes:
        - The NetCDF time coordinate is stored as seconds since the Unix epoch
          using the mean of `Date1` and `Date2` across all observations.
        - Global attributes `date_created`, `time_coverage_start`, and
          `time_coverage_end` are updated after dataset creation.
        - Cropping is based on finite values of `sea_ice_speed`
          at time index 0.
        - Duplicate (i, j) assignments are detected and logged; the last value
          written will overwrite earlier ones for that grid cell.
    """

    import os
    import numpy as np
    import pandas as pd
    from datetime import datetime
    import xarray as xr
    import logging
   
    
    
    # standardize date/time stamps
    df_copy = df.copy()
    df_copy['Date1'] = pd.to_datetime(df_copy['Date1'])
    df_copy['Date2'] = pd.to_datetime(df_copy['Date2'])

    
    # take the starting longitude and latitude that correspond
    # with the start date
    lons = df_copy["Lon1"].to_numpy(dtype=float)
    lats = df_copy["Lat1"].to_numpy(dtype=float)
    
    
    # get the i,j coordinates based on lon/lat
    i, j = _polar_lonlat_to_ij(
        lons,
        lats,
        grid_size=12.5,
        hemisphere="north"
    )    
    # force numpy integer arrays
    i = np.asarray(i, dtype=np.int64)
    j = np.asarray(j, dtype=np.int64)
    
    i_list = [int(val) for val in i]
    j_list = [int(val) for val in j]

    
    # template data set settings
    x_coords = template_ds['x'].values
    y_coords = template_ds['y'].values
    grid_shape = (1, template_ds.sizes['y'], template_ds.sizes['x'])

    
    try:       
        # time defaults
        # convert to "seconds since 1970-01-01 00:00:00"
        # take min time since using Lon1/Lat1

        epoch = pd.Timestamp("1970-01-01 00:00:00")
        min_time = df_copy['Date1'].min()
        max_time = df_copy['Date2'].max()        
        time_sec = (min_time - epoch).total_seconds()
        time_array = np.array([time_sec], dtype='float64')
        
        
        # set NetCDF standard attributes
        meta_ds = _set_metadata(config)
        
       
        # replace placeholders with real values
        # keep attrs from the CDL skeleton
        global_attrs = meta_ds.attrs.copy()
        sea_ice_speed_attrs = meta_ds["sea_ice_speed"].attrs.copy()
        sea_ice_x_attrs = meta_ds["sea_ice_x_displacement"].attrs.copy()
        sea_ice_y_attrs = meta_ds["sea_ice_y_displacement"].attrs.copy()
        direction_attrs = (
            meta_ds["direction_of_sea_ice_displacement"].attrs.copy()
        )
        outlier_attrs = (
            meta_ds["outlier_category"].attrs.copy()
        )
        spatial_ref_attrs = meta_ds["spatial_ref"].attrs.copy()
        x_attrs = meta_ds["x"].attrs.copy()
        y_attrs = meta_ds["y"].attrs.copy()
        time_attrs = meta_ds["time"].attrs.copy()

        meta_ds.close()
        del meta_ds
        
        
        # create dataset from CDL
        netcdf_grid = xr.Dataset(
            data_vars={
                "sea_ice_speed": (
                    ("time", "y", "x"),
                    np.full(grid_shape, np.nan, dtype=np.float32),
                    sea_ice_speed_attrs,
                ),
                "sea_ice_x_displacement": (
                    ("time", "y", "x"),
                    np.full(grid_shape, np.nan, dtype=np.float32),
                    sea_ice_x_attrs,
                ),
                "sea_ice_y_displacement": (
                    ("time", "y", "x"),
                    np.full(grid_shape, np.nan, dtype=np.float32),
                    sea_ice_y_attrs,
                ),
                "direction_of_sea_ice_displacement": (
                    ("time", "y", "x"),
                    np.full(grid_shape, np.nan, dtype=np.float32),
                    direction_attrs,
                ),
                "outlier_category": (
                    ("time", "y", "x"),
                    np.full(grid_shape, -9, dtype=np.int16),
                    outlier_attrs,
                ),                
                "spatial_ref": (
                    (),
                    np.int32(0),
                    spatial_ref_attrs,
                ),
            },
            coords={
                "time": ("time", time_array, time_attrs),
                "x": ("x", x_coords, x_attrs),
                "y": ("y", y_coords, y_attrs),
            },
            attrs=global_attrs,
        )

        # update date and time
        netcdf_grid.attrs['date_created'] = (
            datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
            )
        netcdf_grid.attrs['time_coverage_start'] = (
            min_time.strftime('%Y-%m-%dT%H:%M:%SZ')
            )
        netcdf_grid.attrs['time_coverage_end'] = (
            max_time.strftime('%Y-%m-%dT%H:%M:%SZ')
            )
        
        
        # update NetCDF with values from input data
        idx_list = []
        seen_key = set()
        for row_n, row in enumerate(df_copy.itertuples(index=False)):
            ix = int(i[row_n])   # x index
            iy = int(j[row_n])   # y index
            index_key = (ix, iy)
            idx_list.append(index_key)
            
            if index_key in seen_key:
                print(f'Duplcate entry found for {ix}, {iy}')
                
            seen_key.add(index_key)
        
            netcdf_grid["sea_ice_speed"].values[0, iy, ix] = (
                np.float32(row.Speed_ms)
            )
            netcdf_grid["sea_ice_x_displacement"].values[0, iy, ix] = (
                np.float32(row.U_vel_ms)
            )
            netcdf_grid["sea_ice_y_displacement"].values[0, iy, ix] = (
                np.float32(row.V_vel_ms) # negate to match flipped grid y-axis
            )
            netcdf_grid["direction_of_sea_ice_displacement"].values[
                0, iy, ix
            ] = np.float32(row.Bear_deg)
            netcdf_grid["outlier_category"].values[
                0, iy, ix
            ] = np.int16(row.outlier_category)
        
        
        # update scene_i_j
        scene_i_j[base_name] = list(zip(i_list, j_list))
        
        # crop to populated values
        data_mask = np.isfinite(netcdf_grid["sea_ice_speed"].values[0])
        if np.any(data_mask):
            filled_y, filled_x = np.where(data_mask)
        
            y_start = int(filled_y.min())
            y_end = int(filled_y.max())
            x_start = int(filled_x.min())
            x_end = int(filled_x.max())
        
            # pad grid cells in case vectors extend outside of viewing area
            pad_cells = 4
            y_start = max(0, y_start - pad_cells)
            y_end = min(netcdf_grid.sizes["y"] - 1, y_end + pad_cells)
            x_start = max(0, x_start - pad_cells)
            x_end = min(netcdf_grid.sizes["x"] - 1, x_end + pad_cells)
        
            netcdf_grid = netcdf_grid.isel(
                y=slice(y_start, y_end + 1),
                x=slice(x_start, x_end + 1)
            )
    
        
        # Save to NetCDF with compression level 4     
        output_file_path = os.path.join(
            config['nc_dir'], f"{base_name}.nc"
        )
        netcdf_grid.to_netcdf(
            output_file_path, mode='w',
            encoding={
                'sea_ice_speed': {
                    'zlib': True, 'complevel': 4, 'dtype': 'float32'
                },
                'sea_ice_x_displacement': {
                    'zlib': True, 'complevel': 4, 'dtype': 'float32'
                },
                'sea_ice_y_displacement': {
                    'zlib': True, 'complevel': 4, 'dtype': 'float32'
                },
                'direction_of_sea_ice_displacement': {
                    'zlib': True, 'complevel': 4, 'dtype': 'float32'
                },
                'outlier_category': {
                    'zlib': True, 'complevel': 4, 'dtype': 'int16',
                    '_FillValue': np.int16(-9)
                },
                'spatial_ref': {'dtype': 'int32'}
            }
        )
        
        # log activity
        logger = logging.getLogger('sar_drift_converter')
        logger.info(f'Created NetCDF {output_file_path}')
        
    finally:
        # Ensure that these lines are executed even if an error occurs
        netcdf_grid.close()
        del netcdf_grid


def create_shape_package(df, base_name, config):
    """
    Create a GeoPackage containing drift line vectors for SAR drift data.

    Builds LineString geometries from start to end coordinates and writes
    them to a single layer within a GeoPackage. Longitudes in the 0-360
    range are normalized to -180/180 before geometry creation.

    Args:
        df (pandas.DataFrame): Input DataFrame containing drift vectors.
            Expected columns:
                - 'Lon1', 'Lat1' (float): Starting longitude/latitude
                                          (degrees).
                - 'Lon2', 'Lat2' (float): Ending longitude/latitude (degrees).
                Additional columns are preserved and written to the GeoPackage.
        base_name (str): Base filename (without extension) used to name the
            output GeoPackage file `<config['gpkg_dir']>/<base_name>.gpkg`.
        config (dict): Configuration dictionary containing:
                - 'gpkg_dir' (str): Output directory where the GeoPackage
                                    is written.
                - 'qml_file' (str): Path to the QML style file to embed.

    Returns:
        None

    Notes:
        - CRS is set to EPSG:4326 (geographic lat/lon).
        - A helper column `geometry_type` is added with value 'line'.
        - The QML style is embedded directly into the GeoPackage's
          layer_styles table, so no QML file is needed by end users.
    """

    import os
    import logging
    import geopandas as gpd
    from shapely.geometry import LineString
    
    # add X and Y for EPSG:3411 projection
    df_local = df.copy()
    
    
    tf = _set_transformer()
    df_local['X1'], df_local['Y1'] = tf['4326_to_3413'].transform(
        df_local['Lon1'].values,
        df_local['Lat1'].values
    )
    
    df_local['X2'], df_local['Y2'] = tf['4326_to_3413'].transform(
        df_local['Lon2'].values,
        df_local['Lat2'].values
    )
    
    df_local['geometry_line'] = df_local.apply(
        lambda row: LineString([
            (row['X1'], row['Y1']),
            (
                row['X1'] + row['U_vel_ms'] * row['JS_Duration'],
                row['Y1'] + row['V_vel_ms'] * row['JS_Duration']
            )
        ]),
        axis=1
    )
    
    # Create GeoDataFrame for lines (lines only)
    gdf_line = gpd.GeoDataFrame(
        df_local, geometry='geometry_line'
    )
    # Add a column to distinguish geometry type    
    gdf_line['geometry_type'] = 'line'  
    
   
    # Save as a single GeoPackage file (supports mixed geometries)
    geopackage_file = f"{base_name}.gpkg"
    output_file_path = os.path.join(
        config['gpkg_dir'], f"{geopackage_file}"
    )
    
    gdf_line = gdf_line.rename(
        columns={'geometry_line': 'geometry'}
    ).set_geometry('geometry')
    gdf_line = gdf_line.set_crs(tf['crs_string_3411'])
    gdf_line.to_file(output_file_path, layer='drift_lines', driver='GPKG')
    

    # embed .qml outlier layer style
    _embed_qml_style(output_file_path, 'drift_lines', config['qml_file'])
    
    # log activity
    logger = logging.getLogger('sar_drift_converter')
    logger.info(f'Created GeoPackage {output_file_path}')
    
    
    # *0782308532*0782393500*
        
    
def create_png(config, base_name):
    """
    Create and save a PNG map of sea-ice drift vectors from a NetCDF file.
    
    This function opens a NetCDF dataset (expected to be on a polar 
    stereographic grid consistent with EPSG:3411-like parameters),
    extracts the first time slice of sea-ice displacement components,
    computes vector magnitude, and renders a quiver plot on a Cartopy
    stereographic map. The plot is saved as a PNG file to the directory
    specified in `config`.
    
    Args:
        config (dict): Configuration dictionary containing required paths:
            - 'nc_dir' (str): Directory containing the input NetCDF file.
            - 'png_dir' (str): Directory where the output PNG will be written.
        base_name (str): Base filename (without extension) used to locate the
            NetCDF file (`<nc_dir>/<base_name>.nc`) and name the output PNG
            (`<png_dir>/<base_name>.png`).
    
    Returns:
        None
    
    Expected Dataset Variables:
        - 'x' (1D array): X coordinates in meters (projection coordinates).
        - 'y' (1D array): Y coordinates in meters (projection coordinates).
        - 'sea_ice_x_displacement' (time, y, x): X displacement component.
        - 'sea_ice_y_displacement' (time, y, x): Y displacement component.
        - 'sea_ice_speed' (time, y, x): Used to count finite
          (valid) observations.
    
    Notes:
        - Vector magnitude is computed as `hypot(dx, dy)` and used
          to color the quivers.
        - The map extent is derived from the min/max of the x/y
          coordinate arrays.
        - Quiver scale is adjusted heuristically based on the map span.
        - Requires Cartopy and its dependencies (e.g., PROJ, GEOS).
        - The colorbar label assumes units of meters per day ("m_day")
          and should be updated if the dataset uses different units.
    """
    import xarray as xr
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib.colors as mcolors
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature

    SECONDS_PER_DAY = 86_400 # use this scale to properly show quivers
    source_nc_path = os.path.join(config['nc_dir'], f'{base_name}.nc')
    
    with xr.open_dataset(source_nc_path) as ds:
        x_values = ds['x'].values
        y_values = ds['y'].values
        X, Y = np.meshgrid(x_values, y_values)
        
        dx_values = ds["sea_ice_x_displacement"].isel(time=0).values
        dy_values = ds["sea_ice_y_displacement"].isel(time=0).values

        # determine total valid observations
        arr = ds['sea_ice_speed'].isel(time=0).values
        valid_mask = np.isfinite(arr) # ignore any NaN values
        
        
        outlier_codes = ds['outlier_category'].isel(time=0).values
        outlier_codes = np.asarray(outlier_codes).astype(str)
        
        green_mask = np.isin(outlier_codes, ['00', '01']) & valid_mask
    
    
    
    # set projection defined by data set
    globe_3411 = ccrs.Globe(
        semimajor_axis=6378273.0,
        semiminor_axis=6356889.449
    )
    
    crs_3411 = ccrs.Stereographic(
        central_latitude=90,
        central_longitude=-45,
        false_easting=0.0,
        false_northing=0.0,
        true_scale_latitude=70,
        globe=globe_3411
    )
     
    fig = plt.figure(figsize=(10, 10))
    ax = plt.axes(projection=crs_3411)
    
    # Set extent in the projection's coordinate system (meters)
    pad = 0 # 50km <-- change the pad to change scope of view
    xmin = np.round(x_values.min() - pad, 3)
    xmax = np.round(x_values.max() + pad, 3)
    ymin = np.round(y_values.min() - pad, 3)
    ymax = np.round(y_values.max() + pad, 3)
    
    # set reasonable size of quivers based on dataset extent
    map_width = xmax - xmin
    map_height = ymax - ymin
    map_span = np.round(max(map_height, map_width), 0)
    if map_span > 2_000_000:
        quiver_scale = 0.1
    else:
        quiver_scale = 1.0
    ax.set_extent([xmin, xmax, ymin, ymax], crs=crs_3411)
    
    
    # Coastlines / land
    ax.add_feature(cfeature.LAND, zorder=0)
    ax.coastlines(resolution="10m", linewidth=1.0, zorder=1)
    
    

    mag = np.hypot(dx_values, dy_values) * SECONDS_PER_DAY
    norm = mcolors.Normalize(
        vmin=np.nanmin(mag),
        vmax=np.nanmax(mag)
    )

    q = ax.quiver(
        X[green_mask],
        Y[green_mask],
        dx_values[green_mask] * SECONDS_PER_DAY,
        -dy_values[green_mask] * SECONDS_PER_DAY, # negate back for display
        mag[green_mask],
        transform=crs_3411,
        angles="xy", scale_units="xy",
        scale=quiver_scale,
        width=0.001,
        pivot="tail",
        cmap="viridis",
        norm=norm,
        zorder=2
    )       

    cbar = fig.colorbar(
        q, ax=ax, orientation="vertical", shrink=0.65, pad=0.02
    )
    cbar.set_label("Vector velocity (m_day)")
    
    
    ax.set_title(
        f"Sea-ice Vector Velocities\n"
        f"x {xmin} to {xmax}; y {ymin} to {ymax}\n"
        f"Total observations: {valid_mask.sum()}\n"
        f"Width {np.int32(map_height)} m by Height {np.int32(map_width)} m\n"
        f"Polar stereographic EPSG:3411"
    )
    

    # save plot as .png
    png_file = os.path.join(
        config['png_dir'], f"{base_name}.png"
    )
    fig.savefig(png_file, bbox_inches='tight', dpi=300)
    plt.close(fig)
    
    
def combine_daily_netcdf_files(config, nc_files, template_ds,
                               daily_start_date, daily_end_date,
                               daily_nc_path, multi_layered=True,
                               overwrite=False):
    """
    Combine multiple sliced SAR drift NetCDF files into one full daily mosaic
    on the template grid.

    Parameters
    ----------
    sliced_nc_files (list[str]): Paths to sliced NetCDF scene files.
    template_ds (xarray.Dataset): Template dataset providing the
                                  target grid coordinate arrays and
                                  dimensions.
    daily_start_date (str): YYYYMMDD used to set start time bounds
    daily_end_date (Str): YYYYMMDD used to set start time bounds.
    daily_nc_filename (str): Path to the output daily NetCDF file.
    overwrite : bool, default False
        If False, keep first non-NaN value when overlaps occur.
        If True, later files overwrite earlier files.

    Returns
    -------
    None
    """
    import numpy as np
    import pandas as pd
    import xarray as xr
    from datetime import datetime

    # template grid settings
    # each scene netcdf file will be its own layer
    x_coords = template_ds["x"].values
    y_coords = template_ds["y"].values


    # time defaults for output daily file
    min_time = pd.to_datetime(daily_start_date, format="%Y%m%d")
    max_time = pd.to_datetime(daily_end_date, format="%Y%m%d")   
    if multi_layered:
        n_time = len(nc_files)
    else:
        n_time = 1
    time_array = np.arange(n_time, dtype='float64')
    
    # finalize grid shape
    grid_shape = (n_time, template_ds.sizes["y"], template_ds.sizes["x"])
    
    # track last_write time per cell
    latest_time_grid = np.full(
        (template_ds.sizes["y"], template_ds.sizes["x"]),
        -np.inf,
        dtype=np.float64
    ) 


    # set defaults
    daily_grid = None
    var_names =  [
        "sea_ice_speed",
        "sea_ice_x_displacement",
        "sea_ice_y_displacement",
        "direction_of_sea_ice_displacement",
        "outlier_category"
    ]
    time_list = []
    update_log = []
    

    try:
        # ---------------------------------------------------------
        # Build output dataset from CDL metadata
        # ---------------------------------------------------------
        meta_ds = _set_metadata(config)

        global_attrs = meta_ds.attrs.copy()
        sea_ice_speed_attrs = meta_ds["sea_ice_speed"].attrs.copy()
        sea_ice_x_attrs = meta_ds["sea_ice_x_displacement"].attrs.copy()
        sea_ice_y_attrs = meta_ds["sea_ice_y_displacement"].attrs.copy()
        direction_attrs = (
            meta_ds["direction_of_sea_ice_displacement"].attrs.copy()
        )
        outlier_attrs = meta_ds["outlier_category"].attrs.copy()
        spatial_ref_attrs = meta_ds["spatial_ref"].attrs.copy()
        x_attrs = meta_ds["x"].attrs.copy()
        y_attrs = meta_ds["y"].attrs.copy()
        time_attrs = meta_ds["time"].attrs.copy()

        meta_ds.close()
        del meta_ds
        
        daily_grid = xr.Dataset(
            data_vars={
                "sea_ice_speed": (
                    ("time", "y", "x"),
                    np.full(grid_shape, np.nan, dtype=np.float32),
                    sea_ice_speed_attrs,
                ),
                "sea_ice_x_displacement": (
                    ("time", "y", "x"),
                    np.full(grid_shape, np.nan, dtype=np.float32),
                    sea_ice_x_attrs,
                ),
                "sea_ice_y_displacement": (
                    ("time", "y", "x"),
                    np.full(grid_shape, np.nan, dtype=np.float32),
                    sea_ice_y_attrs,
                ),
                "direction_of_sea_ice_displacement": (
                    ("time", "y", "x"),
                    np.full(grid_shape, np.nan, dtype=np.float32),
                    direction_attrs,
                ),
                "outlier_category": (
                    ("time", "y", "x"),
                    np.full(grid_shape, -9, dtype=np.int16),
                    outlier_attrs,
                ),
                "spatial_ref": (
                    (),
                    np.int32(0),
                    spatial_ref_attrs,
                ),
            },
            coords={
                "time": ("time", time_array, time_attrs),
                "x": ("x", x_coords, x_attrs),
                "y": ("y", y_coords, y_attrs),
            },
            attrs=global_attrs,
        )
        
        # update global attrs
        daily_grid.attrs["date_created"] = (
            datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        )
        daily_grid.attrs["time_coverage_start"] = (
            min_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        )
        daily_grid.attrs["time_coverage_end"] = (
            max_time.strftime("%Y-%m-%dT23:59:59Z")
        )
        
        daily_grid.attrs["title"] = (
            "Daily Northern Hemisphere SAR sea-ice velocity mosaic"
        )
        
        
        """
        For single-layer daily mosaics, deterministic "latest wins" behavior
        for overlapping cells. Do a lightweight first pass to read each
        scene's timestamp, then sort by time (ascending) so later scenes
        are the newest.
        
        For multi-layer output, sorting is optional but keeps layers
        ordered by time.
        """
        file_times = []
        for nc_file in nc_files:
            with xr.open_dataset(nc_file, decode_times=False) as scene_ds:
                file_times.append(
                    (float(scene_ds['time'].values[0]), nc_file)
                )
        file_times.sort(key=lambda x: x[0])
        
        
        # merge each sliced NetCDF into the template grid        
        for nc_idx, (scene_time, nc_file) in enumerate(file_times):
            with xr.open_dataset(
                    nc_file,
                    decode_times=False,
                    mask_and_scale=False
                ) as scene_ds:
                # Note: decode_times=False helps keep units perserved
                # rather than intepreted
                scene_x = scene_ds['x'].values
                scene_y = scene_ds['y'].values
                
                if multi_layered:
                    time_list.append(float(scene_ds['time'].values[0]))
                    t_idx = nc_idx
                else:
                    t_idx = 0
                
                """
                get the start and end x/y to place on template;
                there will be an exact match since the scene was create
                from the template
                """                
                x_start = int(np.where(x_coords == scene_x[0])[0][0])
                x_end   = int(np.where(x_coords == scene_x[-1])[0][0])
                y_start = int(np.where(y_coords == scene_y[0])[0][0])
                y_end   = int(np.where(y_coords == scene_y[-1])[0][0])
                
                # ensure indices are ordered
                x_0, x_1 = min(x_start, x_end), max(x_start, x_end)
                y_0, y_1 = min(y_start, y_end), max(y_start, y_end)
        
                if multi_layered:
                    for var_name in var_names:
                        scene_vals = scene_ds[var_name].isel(time=0).values
                        daily_grid[var_name].values[
                            t_idx, y_0:y_1+1, x_0:x_1+1
                        ] = scene_vals
                else:
                    # Compute write_mask once using the first variable
                    ref_vals = scene_ds[var_names[0]].isel(time=0).values
                    last_t = latest_time_grid[y_0:y_1+1, x_0:x_1+1]
                    valid = np.isfinite(ref_vals)
                    # only if timestamp is later not also the same
                    newer = scene_time > last_t 
                    write_mask = valid & newer
                
                    if write_mask.any():
                        # Log (i,j) updates once — not per variable
                        local_rows, local_cols = np.where(write_mask)
                        for lr, lc in zip(local_rows, local_cols):
                            old_ts = last_t[lr, lc]
                            update_log.append({
                                "i":             y_0 + lr,
                                "j":             x_0 + lc,
                                "old_timestamp": last_t[lr, lc],
                                "new_timestamp": scene_time,
                                "nc_file":       nc_file,
                                "overwrite": old_ts != -np.inf # filter later
                            })
                
                        # Apply write_mask to all variables in one pass
                        for var_name in var_names:
                            scene_vals = scene_ds[var_name].isel(time=0).values
                            target = daily_grid[var_name].values[
                                0, y_0:y_1+1, x_0:x_1+1
                            ]
                            target[write_mask] = scene_vals[write_mask]
                            daily_grid[var_name].values[
                                0, y_0:y_1+1, x_0:x_1+1
                            ] = target
                
                        # Update timestamp tracker once after all variables
                        # are written
                        latest_time_grid[
                            y_0:y_1+1, x_0:x_1+1
                        ][write_mask] = scene_time
                        
                
        # update time array as found in sliced NetCDF files
        if multi_layered:
            time_array = np.array(time_list, dtype='float64')
        else:
            daily_time_sec = (
                pd.to_datetime(daily_start_date, format="%Y%m%d")
                - pd.Timestamp("1970-01-01 00:00:00")
            ).total_seconds()
            time_array = np.array([daily_time_sec], dtype="float64")
            
        daily_grid = daily_grid.assign_coords(
            time=('time', time_array, daily_grid['time'].attrs)
        )

        # save daily NetCDF (compression level 4)
        daily_grid.to_netcdf(
            daily_nc_path,
            mode="w",
            encoding={
                "sea_ice_speed": {
                    "zlib": True, "complevel": 4, "dtype": "float32"
                },
                "sea_ice_x_displacement": {
                    "zlib": True, "complevel": 4, "dtype": "float32"
                },
                "sea_ice_y_displacement": {
                    "zlib": True, "complevel": 4, "dtype": "float32"
                },
                "direction_of_sea_ice_displacement": {
                    "zlib": True, "complevel": 4, "dtype": "float32"
                },
                "outlier_category": {
                    "zlib": True, "complevel": 4, "dtype": "int16",
                    "_FillValue": np.int16(-9)
                },
                "spatial_ref": {"dtype": "int32"},
            }
        )

        if update_log and config['version'] == '00':
            update_df = pd.DataFrame(update_log)
            df_filter = update_df['overwrite']
            update_df = update_df[df_filter].drop(columns='overwrite')
            update_df = update_df.sort_values(['i', 'j'])
            log_path = os.path.join(
                config['output_dir'],
                'cell_update_log.csv'
            )
            update_df.to_csv(log_path, index=False)

    finally:
        if daily_grid is not None:
            daily_grid.close()
            del daily_grid    


def combine_daily_geopackage(gpkg_files, daily_gpkg_path, config):
    """
    Combine multiple scene GeoPackage files into one daily GeoPackage.

    Parameters
    ----------
    gpkg_files (list[str]): Paths to scene GeoPackage files.
    daily_gpkg_path (str): Path to the output daily GeoPackage file.
    config (dict): Configuration dictionary.

    Returns
    -------
    None
    """
    import logging
    import geopandas as gpd

    gdfs = []
    for gpkg_file in gpkg_files:
        gdf = gpd.read_file(gpkg_file, layer='drift_lines')
        gdfs.append(gdf)


    daily_gdf = gpd.pd.concat(gdfs, ignore_index=True)
    daily_gdf = gpd.GeoDataFrame(daily_gdf, geometry='geometry')

    daily_gdf.to_file(daily_gpkg_path, layer='drift_lines', driver='GPKG')
    _embed_qml_style(daily_gpkg_path, 'drift_lines', config['qml_file'])

    logger = logging.getLogger('sar_drift_converter')
    logger.info(
        f'Created daily GeoPackage {daily_gpkg_path} | '
        f'scenes={len(gdfs)} | rows={len(daily_gdf)}'
    )

def overlay_sar_drift_on_geotiff(config, gdf_lines, df_sar, base_name):
    """
    Create a two-panel visualization of SAR sea-ice drift data overlaid 
    on a GeoTIFF image, with both a regional overview map and a detailed 
    drift vector plot.
    
    This function:
        - Loads and displays the SAR backscatter GeoTIFF image
        (projected in EPSG:3413)
        - Plots drift vectors (`dx`, `dy`) as quivers based on line geometries
        - Draws a 50–100 km scale bar for spatial reference
        - Annotates a True North arrow using geodetic conversion
        - Includes a left panel showing a North Polar overview with a red
          rectangle indicating the region of interest
        - Adds axis labels, rotated tick labels, and custom titles
        - Saves the result as a high-resolution PNG image
    
    Parameters:
        geotiff_path (str): Path to the GeoTIFF file representing SAR
                            backscatter imagery.
        gdf_lines (GeoSeries): GeoSeries or list of LineString geometries
                               representing SAR-derived drift vectors.
        df_sar (pandas.DataFrame): DataFrame containing start/end projected
                                   coordinates:
            - 'X1', 'Y1', 'X2', 'Y2': EPSG:3413 coordinates in meters.
        timestamp (str): Timestamp string (e.g., "20250521_1530") for naming
                         the output file.
        sar_basename (str): Short name of the SAR input file,
                            used in the plot title.
        config (dict): Dictionary containing script arguments, including:
            - 'output_dir': Path to the save png
            - 'sar_basename' (str): Base name of the SAR input file,
                                    used for output file names.
    
    Returns:
        matplotlib.figure.Figure: The generated figure with two subplots:
            - Left: Arctic overview with red bounding box
            - Right: Drift vectors overlaid on SAR GeoTIFF
    
    Output:
        A PNG file named `sar_drift_<timestamp>.png` is saved in the current
        working directory.
    
    Notes:
        - The right subplot uses raw Polar Stereographic x/y coordinates
          in meters.
        - The left subplot uses Cartopy’s North Polar Stereographic projection.
        - Only LineString geometries are used for drift vector plotting.
        - The GeoTIFF image must include GCPs or valid transform info
          to be reprojected.
    """
    
    
    import os
    import numpy as np
    import matplotlib.pyplot as plt
    from shapely.geometry import LineString, Polygon
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    from mpl_toolkits.axes_grid1.inset_locator import inset_axes
    
    
    # SAR drift bounds for map extent
    xmin = df_sar[['X1', 'X2']].min().min()
    xmax = df_sar[['X1', 'X2']].max().max()
    ymin = df_sar[['Y1', 'Y2']].min().min()
    ymax = df_sar[['Y1', 'Y2']].max().max()
    
    
    # create buffer around geotiff
    buffer_deg = 10_000 # 10km
    map_extent = [
        xmin - buffer_deg,
        xmax + buffer_deg,
        ymin - buffer_deg,
        ymax + buffer_deg
    ]
    
    map_width = xmax - xmin
    map_height = ymax - ymin
    map_span = np.round(max(map_height, map_width), 0)
    if map_span > 2_000_000:
        quiver_scale = config['quiver_scale_large_area']
    else:
        quiver_scale = config['quiver_scale_small_area']
    
    
    transformer = _set_transformer()

    # initialize plot
    fig = plt.figure(figsize=(18, 10))
    
    if config['create_region_plot']:
        # -------------------------------
        # left map of subplot
        # -------------------------------
        
        # --- overview map with land and coastlines---

        
        # Convert all 4 corners of the SAR extent
        corner_coords = [
            (xmin, ymin),
            (xmax, ymin),
            (xmax, ymax),
            (xmin, ymax),
            (xmin, ymin)  # close the loop
        ]
        
        # transform 3413 to 4326 to draw True North arrow
        corner_lonlat = []
        for x, y in corner_coords:
            corner_lonlat.append(transformer['3413_to_4326'].transform(x, y))
        
        # Create a shapely Polygon and extract x/y separately
        poly = Polygon(corner_lonlat)
        inset_lon, inset_lat = poly.exterior.xy
        
        main_ax = fig.add_subplot(1, 2, 1, projection=ccrs.NorthPolarStereo())
        main_ax.add_feature(cfeature.LAND, zorder=0, facecolor='lightgray')
        main_ax.add_feature(cfeature.COASTLINE, zorder=1)
        main_ax.set_extent([-180, 180, 60, 90], crs=ccrs.PlateCarree())
        gl = main_ax.gridlines(
            draw_labels=True,
            crs=ccrs.PlateCarree(),
            linestyle='--',alpha=0.5
        )
        gl.top_labels = False
        gl.right_labels = False
        gl.xlabel_style = {'size': 10}
        gl.ylabel_style = {'size': 10}
        
        
        # Plot red box on main overview map
        main_ax.plot(
            inset_lon, inset_lat, color='red',
            linewidth=2, transform=ccrs.PlateCarree()
        )
    
        main_ax.set_title('Observation region', fontsize=12)
    
    
    # -------------------------------
    # right map of subplot
    # -------------------------------
        
    # inspired by "+proj=stere +lat_0=90 +lat_ts=70 +lon_0=-45 
    # +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs +type=crs"
    cartopy_crs = ccrs.Stereographic(
        central_latitude=90,
        central_longitude=-45,
        true_scale_latitude=70,
        globe=ccrs.Globe(datum='WGS84')
    )
    
    if config['create_region_plot']:
        # right-side plot
        ax = fig.add_subplot(1, 2, 2, projection=cartopy_crs)
    else:
        # singular plot
        ax = fig.add_subplot(1, 1, 1, projection=cartopy_crs)
        ax.add_feature(cfeature.LAND, zorder=0, facecolor='lightgray')
        ax.add_feature(cfeature.COASTLINE, zorder=1)
        ax.set_extent([-180, 180, 60, 90], crs=cartopy_crs)

    
    
    # read SAR geotiff ansd set graticules
    if config['use_geotiff']:
        masked_xr, map_extent_xr = read_geotiff_rasterio(
            config['sar_geotiff_file']
        )
            
        # plot geotiff    
        ax.imshow(
            masked_xr,
            extent=map_extent_xr,
            origin="upper",
            cmap="gray",
            transform=ccrs.epsg(3413)
        )       
        
        add_graticules(ax, map_extent_xr)
    else:
        gl = ax.gridlines(
            draw_labels=True,
            crs=ccrs.PlateCarree(),
            linestyle='--',alpha=0.5
        )
        gl.top_labels = False
        gl.right_labels = False
        gl.xlabel_style = {'size': 10}
        gl.ylabel_style = {'size': 10}
        
        
    # SAR drift quivers
    # Extract quiver vector data from LineStrings
    lon_start = []
    lat_start = []
    dx = []
    dy = []
    
    for line in gdf_lines:
        if isinstance(line, LineString):
            x0, y0 = line.coords[0]     # start point
            x1, y1 = line.coords[-1]    # end point
            lon_start.append(x0)
            lat_start.append(y0)
            dx.append(x1 - x0)
            dy.append(y1 - y0)
    
    # Plot drift vectors as quivers
    stride = config['vector_stride']
    X = lon_start[::stride]
    Y = lat_start[::stride]
    u = dx[::stride]
    v = dy[::stride]
    mag = np.hypot(u, v) / 1000  # magnitude in km
    Q = ax.quiver(
        X, Y, u, v, mag,
        angles='xy',
        scale_units='xy',
        scale=quiver_scale,
        # scale=0.25,
        width=0.001,
        pivot="tail",
        cmap='viridis'
    )
    
    
    # Create an inset_axes inside ax to match its drawing area better
    cbar_ax = inset_axes(
        ax,
        width="2%",          # width of cbar as percentage of ax width
        height="100%",       # height of cbar as percentage of ax height
        loc='lower left',
        bbox_to_anchor=(1.02, 0., 1, 1),  # position to the right of ax
        bbox_transform=ax.transAxes,
        borderpad=0,
    )
    
    cbar = plt.colorbar(Q, cax=cbar_ax)
    cbar.set_label('Drift Velocity (km/day)', fontsize=10)

    
    # draw scale bar
    add_scale(ax, cartopy_crs)

        
    # True North arrow
    add_true_north(ax, xmin, xmax, ymin, ymax)

    
    # reset map extent
    if config['use_geotiff']:
        ax.set_extent(map_extent_xr, crs=ccrs.epsg(3413))
    else:
        ax.set_extent(map_extent, crs=ccrs.epsg(3413))
    
   
    # titles
    ax.set_title('Velocity Vectors (u, v)', fontsize=12)
    fig.suptitle(
        f"Vector Overlay on GeoTiff:\n{base_name}",
        fontsize=14
    )
    
   
    # save plot as .png
    png_file = os.path.join(
        config['png_dir'], f"{base_name}.png"
    )
    fig.savefig(png_file, bbox_inches='tight', dpi=300)
    plt.close(fig)
        

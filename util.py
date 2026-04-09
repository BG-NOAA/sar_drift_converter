# -*- coding: utf-8 -*-
"""
******************************************************************************

 Project:     SAR Drift COnverter
 Purpose:     Converter SAR drift data into visually interactive output
 Author:      Brendon Gory, brendon.gory@noaa.gov
                            brendon.gory@colostate.edu
              Data Science Application Specialist (Research Associate II)
              at CSU CIRA
 Supervisors: Dr. Ludovic Brucker, ludovic.brucker@noaa.gov
              NESDIS Physical Scientist
              Dr. Prasanjit Dash, prasanjit.dash@noaa.gov
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
        grid_size (float): 6.25, 12.5 or 25; the grid_size cell dimensions in
        km hemisphere ('north' or 'south'): Northern or Southern hemisphere

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
def _set_metadata(config):
    """
    Generate a NetCDF metadata template from an EPSG-specific CDL file
    and load it as an xarray.Dataset.

    Constructs the EPSG-specific CDL filename from the base CDL path in
    config (e.g. 'meta/sar_drift_output.cdl' becomes
    'meta/sar_drift_output_3413.cdl'), runs `ncgen` to convert it to a
    NetCDF file, and loads the result with xarray. The output .nc file is
    named using both the EPSG code and processing level to avoid collisions
    across projections and levels.

    The returned dataset contains only metadata (attributes and structure)
    and is typically used as a template whose attributes are applied to a
    data-driven NetCDF file.

    Parameters:
        config (dict): Configuration dictionary containing:
            - 'netcdf_cdl_file' (str): Path to the base CDL file
                                       (e.g. 'meta/sar_drift_output.cdl').
            - 'epsg' (str | int): EPSG code used to select the correct
                                  CDL file (e.g. 3413).
            - 'level' (str): Processing level used in the output .nc
                             filename (e.g. 'scene', 'daily').

    Returns:
        xarray.Dataset: Dataset containing only metadata from the
                        generated NetCDF file, opened with
                        decode_times=False.

    Raises:
        SystemExit: If the `ncgen` command fails or returns a non-zero
                    exit code.
    """

    import util
    import os
    import subprocess
    import xarray as xr
    
    
    cdl_file = config['netcdf_cdl_file']
    cdl_file_dir = os.path.dirname(cdl_file)
    cdl_file_basename = os.path.basename(cdl_file)
    cdl_file_stem = os.path.splitext(cdl_file_basename)[0]
    epsg_cdl_file = os.path.join(
        cdl_file_dir,
        f'{cdl_file_stem}_{config["epsg"]}.cdl'
    )
    if not os.path.exists(epsg_cdl_file):
        util.error_msg(f"Cannot find `{epsg_cdl_file}`")
        
    ncgen_ofile_nc = os.path.join(
        cdl_file_dir,
        f'{cdl_file_stem}_{config["epsg"]}_{config["level"]}.nc'
    )
    
    
    # Run ncgen command to generate the netCDF file from CDL
    myCmd1 = " ".join(
        [
            "ncgen",
            "-o",
            ncgen_ofile_nc,
            epsg_cdl_file,
        ]
    )
        
    rc = subprocess.call(myCmd1, shell=True)
    if rc != 0:
        error_msg(
            'Error in `ncgen` call. Cannot continue.\n'
            f'Command: {myCmd1}\nError Code: {rc}'
        )
        
    return xr.open_dataset(ncgen_ofile_nc, decode_times=False)


def _calculate_drift_daily(lat1, lon1, lat2, lon2, duration_s, epsg):
    """
    Compute sea-ice drift kinematics from start/end geographic coordinates.
 
    Projects start and end positions from EPSG:4326 to the target projected
    CRS specified by `config['epsg']` (default EPSG:3413, NSIDC Sea Ice Polar
    Stereographic North), computes Cartesian displacement components, and
    derives speed. Bearing is obtained via a WGS84 geodesic inverse
    calculation.
 
    Args:
        lat1 (array-like): Starting latitudes in decimal degrees (EPSG:4326).
        lon1 (array-like): Starting longitudes in decimal degrees (EPSG:4326).
        lat2 (array-like): Ending latitudes in decimal degrees (EPSG:4326).
        lon2 (array-like): Ending longitudes in decimal degrees (EPSG:4326).
        duration_s (array-like): Observation duration in seconds
                                  (Time2_JS − Time1_JS).
        config (dict): Configuration dictionary. Expected keys:
            - 'epsg' (int): EPSG code for the target projected CRS used for
              coordinate transformation and displacement computation
              (e.g. 3413 for NSIDC Sea Ice Polar Stereographic North,
              3411 for NSIDC Polar Stereographic North with Hughes ellipsoid).
 
    Returns:
        dict: Dictionary of derived drift quantities with the following keys:
 
            Projected coordinates (EPSG:`config['epsg']`, meters):
                - 'X1' : x-coordinate of start position
                - 'Y1' : y-coordinate of start position
                - 'X2' : x-coordinate of end position
                - 'Y2' : y-coordinate of end position
 
            Displacement (EPSG:`config['epsg']`, meters):
                - 'dx' : X2 − X1
                - 'dy' : Y2 − Y1
 
            Geodesic quantities (WGS84 ellipsoid):
                - 'distance'  : geodesic distance between start and end (m)
                - 'bearing'   : forward azimuth from start to end (degrees)
 
            Velocity components (EPSG:`config['epsg']`):
                - 'u_ms' : dx / duration_s  (m s⁻¹)
                - 'v_ms' : dy / duration_s  (m s⁻¹)
 
            Speed:
                - 'speed_ms'   : distance / duration_s (m s⁻¹)
                - 'speed_kmdy' : (distance / 1000) / (duration_s / 86400)
                                  (km day⁻¹)
 
    Notes:
        - Projection is performed with `pyproj.Transformer` using
          `always_xy=True`, so longitude is passed before latitude.
        - Geodesic distance and forward azimuth are computed with
          `pyproj.Geod(ellps='WGS84').inv(lon1, lat1, lon2, lat2)`.
        - `u_ms` and `v_ms` are Cartesian velocity components in the target
          projection space. For EPSG:3413 the x-axis points roughly eastward
          and the y-axis roughly northward, but note that the source file's
          `U_vel_ms` / `V_vel_ms` fields use the opposite convention (U drives
          Y, V drives X). The values returned here are computed directly from
          projected displacements and are self-consistent.
        - `speed_ms` and `speed_kmdy` are derived from geodesic distance, not
          from `sqrt(dx² + dy²)`. They are therefore not exactly equal to
          `sqrt(u_ms² + v_ms²)` due to projection distortion; the discrepancy
          is typically ~3–5% at high latitudes.
          
    Coauthor:
        Ludo Brucker, ludovic.brucker@noaa.gov        
    """
    
    import numpy as np
    from pyproj import Transformer, Geod
   
    SECONDS_PER_DAY = 60 * 60 * 24
    tf = Transformer.from_crs('EPSG:4326', f'EPSG:{epsg}', always_xy=True)
    
    x1, y1 = tf.transform(lon1, lat1)
    x2, y2 = tf.transform(lon2, lat2)
   

    dx, dy = np.subtract((x2, y2),(x1, y1))
    distance = np.sqrt(dx**2 + dy**2)

    geod = Geod(ellps='WGS84')
    fwd_azimuth, _ , distance_geod = geod.inv(lon1, lat1, lon2, lat2)
    
    return {
        'X1': x1, 'Y1': y1,
        'X2': x2, 'Y2': y2,
        'dx': dx,
        'dy': dy,
        'distance': distance,
        'distance_geod': distance_geod,
        'bearing': fwd_azimuth,
        'u_ms': dx / duration_s,
        'v_ms': dy / duration_s,
        'speed_ms': distance / duration_s,
        'speed_kmdy': (distance / 1000) / (duration_s / SECONDS_PER_DAY)
    }
        

def _embed_qml_style(gpkg_path, layer_name, config):
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
        config (dict): Configuration dictionary. Must include:
                - 'level' (str): Processing level; controls which QML file
                                 is selected.
                - 'outlier_qml_file' (str): Path to the QML style file used
                                            for level '02' (colors vectors
                                            by outlier category).
                - 'graduated_qml_file' (str): Path to the QML style file
                                              used for all other levels
                                              (colors vectors by displacement
                                              magnitude).

    Returns:
        None

    Notes:
        - The QML file is selected based on config['level']: level '02' uses
          'outlier_qml_file'; all other levels use 'graduated_qml_file'.
        - The layer_styles table is created if it does not already exist,
          following the QGIS standard schema.
        - `f_geometry_column` is hardcoded to 'geom' because GeoPandas
          silently renames the geometry column from 'geometry' to 'geom'
          when writing to GeoPackage format.
        - `styleName` is hardcoded to 'outliers' to satisfy the QGIS
          layer_styles schema; it does not reflect the actual style content.
        - `useAsDefault` is set to 1 so QGIS applies the style automatically
          on load without user intervention.
        - The layer_styles table is registered in gpkg_contents as an
          attributes layer for full GeoPackage spec compliance.
    """
    import sqlite3
    
    if config['level'] == '02':
        qml_path = config['outlier_qml_file']
    else:
        qml_path = config['graduated_qml_file']
    
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
    """
    Compute the circular mean of an array of angles.

    Uses the arctangent of the mean sine and cosine components to correctly
    handle angular wrap-around near 0°/360° (or −π/π radians), where a
    naive arithmetic mean would be incorrect.

    Args:
        a (array-like): Angles in radians. NaN values are ignored.

    Returns:
        float: Circular mean angle in radians, in the range (−π, π].
    """
    
    import numpy as np
    return np.arctan2(np.nanmean(np.sin(a)), np.nanmean(np.cos(a)))


def _circular_std(a):
    """
    Compute the circular standard deviation of an array of angles.
    
    Uses the mean resultant length R — the magnitude of the vector sum of
    unit vectors at each angle — to derive a dispersion measure analogous
    to standard deviation. R = 1 indicates perfect concentration (all angles
    identical); R → 0 indicates maximum dispersion. The circular standard
    deviation is defined as sqrt(−2 · ln(R)), which approaches 0 as
    concentration increases and grows unboundedly as R → 0.
    
    Args:
        a (array-like): Angles in radians. NaN values are ignored.
    
    Returns:
        float: Circular standard deviation in radians, in the range [0, ∞).
            Returns sqrt(−2 · ln(1e-12)) ≈ 7.43 when R is at or below the
            clipping floor of 1e-12 (i.e. maximum dispersion).
    
    Notes:
        - R is clipped to [1e-12, 1.0] before the logarithm to guard against
          log(0) when all angles are maximally dispersed, and against
          log(>1) from floating-point rounding when all angles are identical.
        - Input angles are assumed to be in radians. Degree inputs will
          produce incorrect results.
    """

    import numpy as np
    s = np.nanmean(np.sin(a))
    c = np.nanmean(np.cos(a))
    R = np.sqrt(s*s + c*c)
    return np.sqrt(-2 * np.log(np.clip(R, 1e-12, 1.0)))
    
    
#=========
# Data I/O
#=========

def read_sar_drift_data_file(input_file, config, skip_rows=None):
    """
    Read and preprocess a SAR ice-drift text data file into a standardized
    DataFrame.
    
    This function loads a SAR drift data file (CSV-like text) using parsing
    rules provided in `config`, cleans column names, and derives projected
    coordinates, displacement, velocity, speed, and sensor identifier fields.
    Several raw source columns are renamed for consistency with NetCDF/
    GeoPackage output naming, and columns that are not needed downstream
    are dropped.
    
    Processing steps:
        1. Read the file with `pandas.read_csv()` using delimiter and header
           offsets from `config`.
        2. Strip whitespace from column names.
        3. Convert Julian seconds timestamps (`Time1_JS`, `Time2_JS`) to
           human-readable datetime strings (`date_start`, `date_end`).
        4. Compute observation duration in seconds (`duration_s`).
        5. Project start/end lat/lon to EPSG:`config['epsg']` and compute
           displacement, velocity, speed, bearing, and geodesic distance via
           `_calculate_drift_daily`.
        6. Round all coordinate, displacement, velocity, speed, bearing, and
           distance fields according to precision keys in `config`.
        7. Extract sensor identifiers from `File1`/`File2` into `sensor1`/
           `sensor2`.
        8. Rename geographic coordinate columns:
               Lat1 → latitude_1,  Lon1 → longitude_1
               Lat2 → latitude_2,  Lon2 → longitude_2
        9. Drop source columns that are not used in any output:
               Time1_JS, Time2_JS, U_vel_ms, V_vel_ms, Speed_kmdy, Bear_deg,
               img1_mean, img1_std, img2_mean, img2_std, img1s_mean, img1s_std,
               Npnt, Offset1, Offset2
    
    Args:
        input_file (str or pathlib.Path): Path to the SAR drift data file
                                          to read.
        config (dict): Parsing and precision configuration. Expected keys:
            - 'delimiter' (str): Field delimiter passed to `pd.read_csv`.
            - 'skip_rows_before_header' (int): Number of rows to skip before
              the header row.
            - 'epsg' (int): EPSG code for the target projected CRS used by
              `_calculate_drift_daily` (e.g. 3413 for NSIDC Sea Ice Polar
              Stereographic North). Controls the projection used for X1, Y1,
              X2, Y2, dx, dy, u_ms, and v_ms.
            - 'coordinate_precision' (int): Decimal places for geographic
              coordinates (Lat1, Lon1, Lat2, Lon2) and projected coordinates
              (X1, Y1, X2, Y2).
            - 'displacement_precision' (int): Decimal places for
              `sea_ice_x_displacement`, `sea_ice_y_displacement`, `u_ms`,
              and `v_ms`.
            - 'speed_precision' (int): Decimal places for `sea_ice_speed`,
              `sea_ice_speed_kmdy`, `distance`, and `distance_geod`.
            - 'bearing_precision' (int): Decimal places for
              `direction_of_sea_ice_displacement`.
        skip_rows (list[int] or None): Row indices to skip when reading the
            file, passed directly to `pd.read_csv`. Defaults to None.
    
    Returns:
        pandas.DataFrame: Cleaned and enriched SAR drift DataFrame. Raw source
        columns are preserved (except those listed as dropped above) together
        with the following derived and renamed columns:
    
        Renamed geographic coordinates (rounded to `coordinate_precision`):
            - 'latitude_1'  (float): Starting latitude  (degrees, from Lat1)
            - 'longitude_1' (float): Starting longitude (degrees, from Lon1)
            - 'latitude_2'  (float): Ending latitude    (degrees, from Lat2)
            - 'longitude_2' (float): Ending longitude   (degrees, from Lon2)
    
        Derived timestamps and duration:
            - 'date_start' (str): Start datetime in '%Y-%m-%d %H:%M:%S'
                                  (from Time1_JS)
            - 'date_end'   (str): End datetime in '%Y-%m-%d %H:%M:%S'
                                  (from Time2_JS)
            - 'duration_s' (float): Observation duration in seconds
                                    (Time2_JS - Time1_JS); not rounded.
    
        Projected coordinates (EPSG:`config['epsg']`, meters; rounded to
        `coordinate_precision`):
            - 'X1', 'Y1': Start position
            - 'X2', 'Y2': End position
    
        Displacement and velocity (EPSG:`config['epsg']`; rounded to
        `displacement_precision`):
            - 'sea_ice_x_displacement' (float): X2 - X1  (m)
            - 'sea_ice_y_displacement' (float): Y2 - Y1  (m)
            - 'u_ms' (float): sea_ice_x_displacement / duration_s  (m/s)
            - 'v_ms' (float): sea_ice_y_displacement / duration_s  (m/s)
    
        Speed and direction (rounded to `speed_precision` unless noted):
            - 'sea_ice_speed'      (float): geodesic speed (m/s)
            - 'sea_ice_speed_kmdy' (float): geodesic speed (km/day)
            - 'direction_of_sea_ice_displacement' (float): forward azimuth
                                            (degrees); rounded to
                                            `bearing_precision`
            - 'distance'      (float): projected displacement magnitude (m)
            - 'distance_geod' (float): geodesic great-circle distance (m)
    
        Sensor and scene identifiers:
            - 'scene_id' (str): Combination of 'File1' and 'File2' separated
                                by underscore
            - 'sensor1'  (str): Satellite identifier from File1
                                (prefix before first underscore)
            - 'sensor2'  (str): Satellite identifier from File2
                                (prefix before first underscore)
    
    Notes:
        - SAR time fields `Time1_JS` and `Time2_JS` are seconds since
          2000-01-01 00:00:00.
        - A specific `pyproj` warning about database path setup is suppressed
          because it is expected in this runtime environment.
        - Required source columns: 'Time1_JS', 'Time2_JS', 'Lat1', 'Lon1',
          'Lat2', 'Lon2', 'File1', 'File2'. The columns 'Bear_deg',
          'Speed_kmdy', 'U_vel_ms', 'V_vel_ms' must also be present but are
          dropped after processing.
    """
    
    import numpy as np
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
    df['date_start'] = df["Time1_JS"].apply(
        lambda x: base_time + timedelta(seconds=x)
        )
    df['date_start'] = df['date_start'].dt.strftime('%Y-%m-%d %H:%M:%S')
    df['date_end'] = df["Time2_JS"].apply(
        lambda x: base_time + timedelta(seconds=x)
        )
    df['date_end'] = df['date_end'].dt.strftime('%Y-%m-%d %H:%M:%S')
    

    # Calculate duration of observations in seconds
    df['duration_s'] = (
        df['Time2_JS'] - df['Time1_JS']
    )
    
    drift = _calculate_drift_daily(
        lat1=df['Lat1'].values,
        lon1=df['Lon1'].values,
        lat2=df['Lat2'].values,
        lon2=df['Lon2'].values,
        duration_s=df['duration_s'].values,
        epsg=config['epsg']
    )
    
    df['Lat1'] = np.round(df['Lat1'], config['coordinate_precision'])
    df['Lon1'] = np.round(df['Lon1'], config['coordinate_precision'])
    df['Lat2'] = np.round(df['Lat2'], config['coordinate_precision'])
    df['Lon2'] = np.round(df['Lon2'], config['coordinate_precision'])
    df['X1'] = np.round(drift['X1'], config['coordinate_precision'])
    df['Y1'] = np.round(drift['Y1'], config['coordinate_precision'])
    df['X2'] = np.round(drift['X2'], config['coordinate_precision'])
    df['Y2'] = np.round(drift['Y2'], config['coordinate_precision'])
    df['sea_ice_x_displacement'] = np.round(
        drift['dx'], config['displacement_precision']
    )
    df['sea_ice_y_displacement'] = np.round(
        drift['dy'], config['displacement_precision']
    )
    df['u_ms'] = np.round(drift['u_ms'], config['displacement_precision'])
    df['v_ms'] = np.round(drift['v_ms'], config['displacement_precision'])
    df['sea_ice_speed'] = np.round(
        drift['speed_ms'],
        config['speed_precision']
    )
    df['sea_ice_speed_kmdy'] = np.round(
        drift['speed_kmdy'],
        config['speed_precision']
    )
    df['direction_of_sea_ice_displacement'] = np.round(
        drift['bearing'], config['bearing_precision']
    )
    df['distance'] = np.round(
        drift['distance'], config['speed_precision']
    )
    df['distance_geod'] = np.round(
        drift['distance_geod'], config['speed_precision']
    )
    
    
    # identify satellites for analysis
    df['sensor1'] = df["File1"].str.partition("_")[0]
    df['sensor2'] = df["File2"].str.partition("_")[0]
    df['scene_id'] = df['File1'] + '_' + df['File2']
    
    df.rename(columns=
              {
                  'Lat1': 'latitude_1',
                  'Lon1': 'longitude_1',
                  'Lat2': 'latitude_2',
                  'Lon2': 'longitude_2'
        },
        inplace=True
    )
    
    df.drop(
        [
            'Time1_JS', 'Time2_JS',
            'U_vel_ms', 'V_vel_ms', 'Speed_kmdy', 'Bear_deg',
            'img1_mean', 'img1_std', 'img2_mean', 'img2_std',
            'img1s_mean', 'img1s_std', 'Npnt', 'Offset1', 'Offset2'
        ],
        axis=1,
        inplace=True
    )
    
    return df


def outlier_search(df, config, base_name, radius_km,
                   min_neighbors, md_neighbors, z_score_level,
                   chi_square_level, passes):
    """
    Detect and classify outlier drift vectors within each SAR scene.

    For each scene (grouped by `File1`/`File2`), computes per-vector outlier
    flags using two independent methods: z-score on speed and bearing, and
    Mahalanobis distance on displacement components. Results are combined into
    a two-digit `outlier_category` code encoding outlier type and statistical
    confidence. Detection is run iteratively, excluding already-flagged vectors
    from the neighbor pool on each subsequent pass.

    Args:
        df (pandas.DataFrame): Input drift observations. Expected columns:
                - 'File1', 'File2' (str): Scene pair identifiers used for
                  grouping.
                - 'X1', 'Y1' (float): Projected start coordinates
                  (EPSG:`config['epsg']`, meters); used to build the
                  spatial neighbor index.
                - 'sea_ice_speed' (float): Drift speed (m s⁻¹); used for
                  z-score distance outlier detection.
                - 'direction_of_sea_ice_displacement' (float): Forward azimuth
                  (degrees); used for z-score bearing outlier detection.
                - 'sea_ice_x_displacement', 'sea_ice_y_displacement' (float):
                  Displacement components (m); used as features for
                  Mahalanobis distance outlier detection.
        config (dict): Configuration dictionary. Must include:
                - 'level' (str): Processing level. If '01', outlier detection
                  is skipped and all rows are assigned `outlier_category`
                  of '-9'.
                - 'epsg' (int): EPSG code of the projected CRS used for
                  `X1`/`Y1` coordinates, passed through from
                  `read_sar_drift_data_file`. Used here only for
                  documentation context; the neighbor search operates
                  directly on the projected meter values.
        base_name (str): Scene identifier string used in log messages.
        radius_km (float): Search radius in kilometers for z-score neighbor
                           lookup via `cKDTree.query_ball_point`.
        min_neighbors (int): Minimum number of neighbors required for a
                             z-score outlier flag to be considered
                             statistically confident (i.e. to receive a `1`
                             confidence digit).
        md_neighbors (int): Minimum number of neighbors required for a
                            Mahalanobis distance outlier flag to be considered
                            statistically confident.
        z_score_level (float): Z-score threshold above which a vector is
                               flagged as a speed or bearing outlier.
        chi_square_level (float): Chi-square cumulative probability threshold
                                  (e.g. 0.99) used to derive the squared
                                  Mahalanobis distance cutoff via
                                  `chi2.ppf(chi_square_level, df=2)`.
        passes (int): Maximum number of detection iterations. Each pass
                      rebuilds the neighbor pool using only current inliers
                      (`outlier_category` in `['00', '01']`). Iteration stops
                      early if the inlier count stabilizes between passes.

    Returns:
        pandas.DataFrame: Copy of `df` with the following columns added:
                - 'outlier_category' (str): Two-digit code encoding outlier
                  type (tens digit) and statistical confidence (units digit).
                  See Notes for the full encoding table. Set to '-9' for
                  level '01'.
                - 'scene' (int): Scene group number assigned by
                  `File1`/`File2` pairing.
                - 'sd_neighbor_indices' (list[int]): `out_df` row indices of
                  z-score neighbors for each vector.
                - 'sd_neighbor_count' (int): Number of z-score neighbors found.
                - 'distance_z_score' (float): Absolute z-score of speed
                  relative to neighbors.
                - 'bearing_z_score' (float): Absolute circular z-score of
                  bearing relative to neighbors.
                - 'md_neighbor_indices' (list[int]): `out_df` row indices of
                  Mahalanobis neighbors for each vector.
                - 'md_neighbor_count' (int): Number of Mahalanobis neighbors
                  found.
                - 'mahal_sq' (float): Squared Mahalanobis distance of the
                  vector from its neighbors.
                - 'thr_sq' (float): Squared distance threshold derived from
                  `chi_square_level`.
                - 'mahal_outlier_flag' (bool): True if `mahal_sq > thr_sq`.
                - 'sd_outlier_pass' (int): Pass index (1-based) on which the
                  vector was first flagged by z-score; −1 if never flagged.
                - 'md_outlier_pass' (int): Pass index (1-based) on which the
                  vector was first flagged by Mahalanobis distance; −1 if
                  never flagged.

    Notes:
        **Level '01' short-circuit:** If `config['level']` is '01', the
        function assigns `outlier_category = '-9'` to all rows and returns
        immediately without performing any detection.

        **outlier_category encoding:** The two-digit string combines a tens
        digit for outlier type and a units digit for statistical confidence
        (0 = below neighbor threshold, 1 = at or above threshold):

        | Code | Outlier Type                              |
        |------|-------------------------------------------|
        | `00` | None (under neighbor threshold)           |
        | `01` | None (at or above neighbor threshold)     |
        | `10` | Distance                                  |
        | `11` | Distance (confident)                      |
        | `20` | Bearing                                   |
        | `21` | Bearing (confident)                       |
        | `30` | Mahalanobis distance                      |
        | `31` | Mahalanobis distance (confident)          |
        | `40` | Distance and bearing                      |
        | `41` | Distance and bearing (confident)          |
        | `50` | Mahalanobis distance and distance         |
        | `51` | Mahalanobis distance and distance (conf.) |
        | `60` | Mahalanobis distance and bearing          |
        | `61` | Mahalanobis distance and bearing (conf.)  |
        | `70` | Mahalanobis distance, distance and bearing|
        | `71` | Mahalanobis distance, distance and bearing (conf.) |

        **Confidence digit:** For categories involving Mahalanobis distance
        (30–71), confidence uses `md_neighbors`; for all others it uses
        `min_neighbors`.

        **Mahalanobis estimation:** Uses `LedoitWolf` covariance on
        standardized displacement components, which is more stable than
        `MinCovDet` for small or ill-conditioned neighbor samples. Vectors
        with fewer than `max(2p+1, md_neighbors)` neighbors or a rank-
        deficient neighbor matrix receive `mahal_sq = NaN` and are not
        flagged.

        **Bearing z-score:** Computed using circular statistics —
        `arctan2(sin(Δ), cos(Δ))` normalizes the angular difference before
        dividing by circular standard deviation, correctly handling wrap-
        around near 0°/360°.

        **Iterative passes:** On each pass, the neighbor pool is restricted
        to current inliers only, preventing flagged vectors from inflating
        local statistics. Iteration stops early if the inlier count does not
        change between passes.
    """
    
    import numpy as np
    import logging
    from scipy.spatial import cKDTree
    from sklearn.covariance import LedoitWolf
    from scipy.stats import chi2
    
    if config['level'] == '01':
        # no outlier deteection required
        df['outlier_category'] = '-9'
        return df
    

    out_df = df.reset_index(drop=True).copy()
    
    radius_m = radius_km * 1000
    iter_prev_inliers = None
    
    # create scene groupings based on `File` and `File2` values
    out_df = out_df.sort_values(by=['File1', 'File2'], ascending=True)
    out_df = out_df.reset_index(drop=True) # reset index after sorting
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
            Xall = scene_df[
                ['sea_ice_x_displacement', 'sea_ice_y_displacement']
            ].to_numpy()

            
            for local_idx, local_neighbors in enumerate(all_neighbors):
                
                # drop self
                neigh_idxs = [
                    j for j in local_neighbors if j != local_idx
                ]
                
                target_out_idx = scene_df.index[local_idx]
                
                if len(neigh_idxs) == 0:
                    continue
                
                neigh_rows = scene_df.iloc[neigh_idxs]

                neigh_dist = neigh_rows['sea_ice_speed'].to_numpy()
                neigh_bear = (
                    neigh_rows['direction_of_sea_ice_displacement'].to_numpy()
                )
                
                
                # compute neighbor mean and standard deviation
                dist_mean = np.nanmean(neigh_dist)
                dist_std = np.nanstd(neigh_dist)
                bear_mean = _circular_mean(neigh_bear)
                bear_std = _circular_std(neigh_bear)
                
                # get current cell values
                cell_dist = scene_df.iloc[local_idx]['sea_ice_speed']
                cell_bear = (
                    scene_df.iloc[local_idx]
                    ['direction_of_sea_ice_displacement']
                )
                
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
            
            logger = logging.getLogger('sar_drift_converter')
            logger.info(
                f"Scene {base_name} | Pass {pass_idx + 1} | "
                f"total={total} | inliers={n_inliers} | "
                f"outliers={n_outliers} | distance={n_distance} | "
                f"bearing={n_bearing} | mahalanobis={n_md} | "
                f"dist+bear={n_d_b} | md+dist={n_md_d} | "
                f"md+bear={n_md_b} | md+dist+bear={n_md_d_b}"
            )
        
    
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
            Expected columns (as produced by `read_sar_drift_data_file`):
                - 'date_start' (datetime-like): Start timestamp for the vector.
                - 'date_end' (datetime-like): End timestamp for the vector.
                - 'duration_s' (float): Observation duration in seconds.
                - 'longitude_1' (float): Starting longitude (degrees,
                  EPSG:4326); used to locate each vector on the NSIDC 12.5 km
                  polar stereographic grid regardless of the projected CRS
                  used for displacement computation.
                - 'latitude_1' (float): Starting latitude (degrees, EPSG:4326).
                - 'sea_ice_speed' (float): Sea-ice speed (m s⁻¹); derived
                  from the projected CRS specified by `config['epsg']`
                  upstream.
                - 'sea_ice_x_displacement' (float): X displacement (m);
                  projected in `config['epsg']` CRS.
                - 'sea_ice_y_displacement' (float): Y displacement (m);
                  projected in `config['epsg']` CRS.
                - 'direction_of_sea_ice_displacement' (float): Bearing
                  (degrees); geodesic, independent of projected CRS.
                - 'outlier_category' (str): Two-digit outlier classification
                  code (e.g. '00', '01', '11'). For level '03', only rows
                  with values '00' or '01' are retained and the value is
                  recoded to −1 before writing.
                - 'Maxcorr1', 'Maxcorr2' (float): Cross-correlation scores
                  (used for `measurement_error` flag in levels '00'/'01').
                - '_use_75km' (bool): Whether the 75 km file was used
                  (controls speed threshold for `speed_error` flag).
        base_name (str): Base filename (without extension) used to name
                         the output NetCDF file
                         `<config['nc_dir']>/<base_name>.nc`.
        config (dict): Configuration dictionary. Must include:
                - 'nc_dir' (str): Output directory where the NetCDF file
                                  is written.
                - 'level'  (str): Processing level ('00'–'03'); controls
                                  inlier filtering, error flag computation,
                                  and fill value assignment.
                - 'epsg' (int): EPSG code of the projected CRS used upstream
                                for displacement and speed computation.
                                Does not affect the output grid, which is
                                always the NSIDC 12.5 km polar stereographic
                                grid (EPSG:3413).
        template_ds (xarray.Dataset): Template dataset providing the target
                                      grid coordinate arrays and dimensions.
        scene_i_j (dict): Mutable dictionary updated in-place with the list
                          of (i, j) grid index pairs for this scene, keyed
                          by `base_name`.
 
    Returns:
        str: Path to the written NetCDF file
             (`<config['nc_dir']>/<base_name>.nc`). Returns `None` early
             if level is '03' and no rows survive the inlier filter.
 
    Workflow:
        1. Parse `date_start` and `date_end` to pandas datetimes.
        2. For level '03': retain only rows where `outlier_category` is '00'
           or '01' (inliers), recode `outlier_category` to −1, and return
           early if no rows survive.
        3. Derive the scene reference time and time bounds from `duration_s`,
           `date_start`, and `date_end`.
        4. Compute error flags (`bearing_error`, `speed_error`,
           `measurement_error`) for levels '00'/'01'; set to −9 otherwise.
        5. Convert starting positions (`longitude_1`, `latitude_1`) to NSIDC
           12.5 km polar stereographic grid indices (i, j) using
           `_polar_lonlat_to_ij`. Grid placement always uses EPSG:4326
           geographic coordinates and is independent of `config['epsg']`.
        6. Load CDL-derived variable and global attributes from
           `_set_metadata(config)`.
        7. Build an `xarray.Dataset` on the full template grid, initialised
           with NaN / −9 fill values.
        8. Populate the time slice at index 0 with per-observation values for
           all science and flag variables.
        9. Crop the dataset to the bounding box of finite `sea_ice_speed`
           values, with a 4-cell padding on each side.
       10. Write to NetCDF with zlib compression (level 4) and explicit
           `_FillValue` / dtype encoding per variable.
 
    Notes:
        - The output grid is always the NSIDC 12.5 km polar stereographic
          grid (EPSG:3413), regardless of the `config['epsg']` value used
          for upstream displacement computation.
        - The `time` coordinate is set to the minimum `date_start` value
          across all observations, stored as seconds since 2000-01-01
          (Julian seconds, matching the source file convention).
        - `time_bnds` spans [min(date_start), max(date_end)] for the scene.
        - Global attributes `date_created`, `time_coverage_start`, and
          `time_coverage_end` are updated after dataset construction.
        - Duplicate (i, j) assignments are detected and logged; the last
          observation written wins for that grid cell.
        - All int16 flag variables use −9 as their `_FillValue`. For level
          '03', `outlier_category` carries −1 for all written observations,
          indicating the outlier algorithm has been applied and the vector
          passed as an inlier.
    """
 
    import os
    import numpy as np
    import pandas as pd
    from datetime import datetime
    import xarray as xr
    import logging
 
 
    # standardize date/time stamps
    df_copy = df.copy()
    df_copy['date_start'] = pd.to_datetime(df_copy['date_start'])
    df_copy['date_end'] = pd.to_datetime(df_copy['date_end'])
    
    
    # For level 03, retain only inlier vectors (outlier_category 00 or 01),
    # then recode to -1 to signal that outlier filtering has been applied.
    if config['level'] == '03':
        outlier_filter = df_copy['outlier_category'].isin(['00', '01'])
        df_copy = df_copy[outlier_filter].copy()
        
        df_copy['outlier_category'] = -1
        if df_copy.shape[0] == 0:
            # it might be possible the data frame was labelled
            # as all outliers.
            return None
    
    layer_id_str = df_copy['scene_id'].iloc[0]
 
    # use minimum date_start as scene reference time (Julian seconds)
    # reconstruct Time1_JS from date_start relative to 2000-01-01
    epoch = pd.Timestamp('2000-01-01')
    time_sec = float(
        (df_copy['date_start'].min() - epoch).total_seconds()
    )
    time_array = np.array([time_sec], dtype='float64')
 
    # time bounds: [min date_start, max date_end] in Julian seconds
    time_bounds = np.array([
        [time_sec,
         float((df_copy['date_end'].max() - epoch).total_seconds())]
    ], dtype='float64')
 
    min_time = df_copy['date_start'].min()
    max_time = df_copy['date_end'].max()
 
    # compute error flags for levels 00/01; set fill value otherwise
    if config['level'] in ['00', '01']:
        # bearing check: 0 if valid, 1 if invalid
        df_filter = (
            (df_copy['direction_of_sea_ice_displacement'] != 0) &
            (df_copy['sea_ice_speed'] > 0)
        )
        df_copy['bearing_error'] = (~df_filter).astype(int)
 
        # speed check: 0 if valid, 1 if invalid
        speed_thresh = 35.0 if df_copy['_use_75km'].iloc[0] else 25.0
        df_filter = (df_copy['sea_ice_speed'] < speed_thresh)
        df_copy['speed_error'] = (~df_filter).astype(int)
 
        # Maxcorr2 > Maxcorr1 check: 0 if valid, 1 if invalid
        df_filter = (df_copy['Maxcorr1'] > df_copy['Maxcorr2'])
        df_copy['measurement_error'] = df_filter.astype(int)
    else:
        df_copy['bearing_error'] = -9
        df_copy['speed_error'] = -9
        df_copy['measurement_error'] = -9
 
    # use starting position (longitude_1, latitude_1) to locate grid cells
    lons = df_copy["longitude_1"].to_numpy(dtype=float)
    lats = df_copy["latitude_1"].to_numpy(dtype=float)
 
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
        # set NetCDF standard attributes from CDL template
        meta_ds = _set_metadata(config)
        

     
        # keep attrs from the CDL skeleton
        global_attrs = meta_ds.attrs.copy()
        sea_ice_speed_attrs = meta_ds["sea_ice_speed"].attrs.copy()
        sea_ice_x_attrs = meta_ds["sea_ice_x_displacement"].attrs.copy()
        sea_ice_y_attrs = meta_ds["sea_ice_y_displacement"].attrs.copy()
        direction_attrs = (
            meta_ds["direction_of_sea_ice_displacement"].attrs.copy()
        )
        outlier_attrs = meta_ds["outlier_category"].attrs.copy()
        bearing_error_attrs = meta_ds["bearing_error"].attrs.copy()
        speed_error_attrs = meta_ds["speed_error"].attrs.copy()
        measurement_error_attrs = meta_ds["measurement_error"].attrs.copy()
        spatial_ref_attrs = meta_ds["spatial_ref"].attrs.copy()
        x_attrs = meta_ds["x"].attrs.copy()
        y_attrs = meta_ds["y"].attrs.copy()
        time_attrs = meta_ds["time"].attrs.copy()
        layer_id_attrs = meta_ds["layer_id"].attrs.copy()
        time_attrs['coordinates'] = 'layer_id'
            
        meta_ds.close()
        del meta_ds
     
        # create dataset from CDL
        netcdf_grid = xr.Dataset(
            data_vars={
                "sea_ice_speed": (
                    ("time", "y", "x"),
                    np.full(grid_shape, np.nan, dtype=np.float32),
                    sea_ice_speed_attrs
                ),
                "sea_ice_x_displacement": (
                    ("time", "y", "x"),
                    np.full(grid_shape, np.nan, dtype=np.float32),
                    sea_ice_x_attrs
                ),
                "sea_ice_y_displacement": (
                    ("time", "y", "x"),
                    np.full(grid_shape, np.nan, dtype=np.float32),
                    sea_ice_y_attrs
                ),
                "direction_of_sea_ice_displacement": (
                    ("time", "y", "x"),
                    np.full(grid_shape, np.nan, dtype=np.float32),
                    direction_attrs
                ),
                "outlier_category": (
                    ("time", "y", "x"),
                    np.full(grid_shape, -9, dtype=np.int16),
                    outlier_attrs
                ),
                "bearing_error": (
                    ("time", "y", "x"),
                    np.full(grid_shape, -9, dtype=np.int16),
                    bearing_error_attrs
                ),
                "speed_error": (
                    ("time", "y", "x"),
                    np.full(grid_shape, -9, dtype=np.int16),
                    speed_error_attrs
                ),
                "measurement_error": (
                    ("time", "y", "x"),
                    np.full(grid_shape, -9, dtype=np.int16),
                    measurement_error_attrs
                ),
                "spatial_ref": (
                    (),
                    np.int32(0),
                    spatial_ref_attrs
                ),
                "time_bnds": (
                    ("time", "nv"),
                    time_bounds
                )
            },
            coords={
                "time": ("time", time_array, time_attrs),
                "layer_id": (
                    "time",
                    np.array([layer_id_str]),
                    layer_id_attrs
                ),
                "nv": [0, 1],
                "x": ("x", x_coords, x_attrs),
                "y": ("y", y_coords, y_attrs)
            },
            attrs=global_attrs
        )
     
        # update global date/time coverage attributes
        netcdf_grid.attrs['date_created'] = (
            datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        )
        netcdf_grid.attrs['time_coverage_start'] = (
            min_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        )
        netcdf_grid.attrs['time_coverage_end'] = (
            max_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        )
     
     
        # populate grid with per-observation values
        idx_list = []
        seen_key = set()
        for row_n, row in enumerate(df_copy.itertuples(index=False)):
            ix = int(i[row_n])   # x index
            iy = int(j[row_n])   # y index
            index_key = (ix, iy)
            idx_list.append(index_key)
     
            if index_key in seen_key:
                print(f'Duplicate entry found for {ix}, {iy}')
     
            seen_key.add(index_key)
     
            netcdf_grid["sea_ice_speed"].values[0, iy, ix] = (
                np.float32(row.sea_ice_speed)
            )
            netcdf_grid["sea_ice_x_displacement"].values[0, iy, ix] = (
                np.float32(row.sea_ice_x_displacement)
            )
            netcdf_grid["sea_ice_y_displacement"].values[0, iy, ix] = (
                np.float32(row.sea_ice_y_displacement)
            )
            netcdf_grid["direction_of_sea_ice_displacement"].values[
                0, iy, ix
            ] = np.float32(row.direction_of_sea_ice_displacement)
            netcdf_grid["outlier_category"].values[
                0, iy, ix
            ] = np.int16(row.outlier_category)
            netcdf_grid["bearing_error"].values[
                0, iy, ix
            ] = np.int16(row.bearing_error)
            netcdf_grid["speed_error"].values[
                0, iy, ix
            ] = np.int16(row.speed_error)
            netcdf_grid["measurement_error"].values[
                0, iy, ix
            ] = np.int16(row.measurement_error)
     
     
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
     
     
        # save to NetCDF with zlib compression level 4
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
                'bearing_error': {
                    'zlib': True, 'complevel': 4, 'dtype': 'int16',
                    '_FillValue': np.int16(-9)
                },
                'speed_error': {
                    'zlib': True, 'complevel': 4, 'dtype': 'int16',
                    '_FillValue': np.int16(-9)
                },
                'measurement_error': {
                    'zlib': True, 'complevel': 4, 'dtype': 'int16',
                    '_FillValue': np.int16(-9)
                },
                'time_bnds': {'dtype': 'float64'},
                'spatial_ref': {'dtype': 'int32'}
            }
        )
     
        # log activity
        logger = logging.getLogger('sar_drift_converter')
        logger.info(f'Created NetCDF {output_file_path}')
 
    finally:
        # ensure dataset is closed even if an error occurs
        netcdf_grid.close()
        del netcdf_grid
        
        
    return  os.path.join(config["nc_dir"], f'{base_name}.nc')


def create_shape_package(df, gpkg_path, config):
    """
    Create a GeoPackage containing drift line vectors for SAR drift data.

    Builds LineString geometries from projected start and end coordinates
    (EPSG:`config['epsg']`) and writes them as a single `drift_lines` layer
    within a GeoPackage. A QML style file is embedded directly into the
    GeoPackage's `layer_styles` table for automatic styling when opened in
    QGIS.

    Args:
        df (pandas.DataFrame): Input DataFrame containing drift vectors, as
            produced by `read_sar_drift_data_file` and `outlier_search`.
            Expected columns:
                Projected coordinates (EPSG:`config['epsg']`, metres):
                    - 'X1', 'Y1' (float): Start position.
                    - 'X2', 'Y2' (float): End position.
                Geographic coordinates (degrees):
                    - 'longitude_1', 'latitude_1' (float): Start lon/lat.
                    - 'longitude_2', 'latitude_2' (float): End lon/lat.
                Timestamps and duration:
                    - 'date_start' (str): Start datetime
                                         ('%Y-%m-%d %H:%M:%S').
                    - 'date_end'   (str): End datetime
                                         ('%Y-%m-%d %H:%M:%S').
                    - 'duration_s' (float): Observation duration (s).
                Sensor identifiers:
                    - 'sensor1', 'sensor2' (str): Satellite/sensor IDs.
                Science variables:
                    - 'sea_ice_x_displacement' (float): X displacement (m).
                    - 'sea_ice_y_displacement' (float): Y displacement (m).
                    - 'u_ms' (float): X velocity component (m s⁻¹).
                    - 'v_ms' (float): Y velocity component (m s⁻¹).
                    - 'sea_ice_speed' (float): Drift speed (m s⁻¹).
                    - 'sea_ice_speed_kmdy' (float): Drift speed (km day⁻¹).
                    - 'direction_of_sea_ice_displacement' (float): Forward
                                                                   azimuth
                                                                   (degrees).
                    - 'distance'      (float): Euclidean displacement distance
                                               in projected space:
                                               sqrt(dx² + dy²) (m).
                    - 'distance_geod' (float): Geodesic distance on the WGS84
                                               ellipsoid (m). Present in the
                                               GeoPackage.
                Outlier flag (level-dependent):
                    - 'outlier_category' (str): Two-digit outlier code;
                      included when config['level'] in ['00', '02', '03'].
                      For level '03', only rows with values '00' or '01' are
                      retained and the value is recoded to −1 before writing.
        gpkg_path (str): Full path for the output GeoPackage file.
        config (dict): Configuration dictionary containing:
                - 'epsg' (int): EPSG code of the projected CRS used for
                                `X1`, `Y1`, `X2`, `Y2` coordinates and set
                                as the GeoPackage layer CRS.
                - 'level' (str): Processing level; controls whether
                                 `outlier_category` is included
                                 ('00', '02', or '03' = include, otherwise
                                 omit) and whether inlier filtering is
                                 applied ('03' only).
                - 'outlier_qml_file' (str): Path to the QML style file used
                                            for level '02' (colors vectors
                                            by outlier category).
                - 'graduated_qml_file' (str): Path to the QML style file
                                              used for all other levels
                                              (colors vectors by displacement
                                              magnitude).

    Returns:
        None
        
    Notes:
        - Geometry is a `LineString` from `(X1, Y1)` to `(X2, Y2)` in
          EPSG:`config['epsg']` projected metres, not from geographic
          coordinates.
        - CRS is set to EPSG:`config['epsg']`.
        - A helper column `geometry_type` is added with the literal value
          `'line'` to identify the layer geometry type.
        - Only the columns listed in `needed_cols` (plus `outlier_category`
          where applicable) are written; all other DataFrame columns are
          excluded.
        - The QML style is embedded via `_embed_qml_style`, so end users do
          not need the QML file present to load the styled layer in QGIS.
    """

    import logging
    import geopandas as gpd
    from shapely.geometry import LineString
    
    df_local = df.copy()

    # keep necessary columns for GeoPackage
    needed_cols = [
        'scene_id', 'sensor1', 'sensor2',
        'longitude_1', 'latitude_1', 'longitude_2', 'latitude_2',
        'X1', 'Y1', 'X2', 'Y2',
        'date_start', 'date_end', 'duration_s',
        'sea_ice_x_displacement', 'sea_ice_y_displacement',
        'u_ms', 'v_ms','sea_ice_speed', 'sea_ice_speed_kmdy',
        'direction_of_sea_ice_displacement', 'distance', 'distance_geod'
    ]
    
    if config['level'] in ['00', '02', '03']:
        needed_cols.append('outlier_category')
        
    df_local=df_local[needed_cols]
    
    
    # For level 03, retain only inlier vectors (outlier_category 00 or 01),
    # then recode to -1 to signal that outlier filtering has been applied.
    if config['level'] == '03':
        outlier_filter = df_local['outlier_category'].isin(['00', '01'])
        df_local = df_local[outlier_filter].copy()
        df_local['outlier_category'] = -1
        if df_local.shape[0] == 0:
            # it might be possible the data frame was labelled
            # as all outliers.
            return None
    
    df_local['geometry_line'] = df_local.apply(
        lambda row: LineString(
            [
                (row['X1'], row['Y1']),
                (row['X2'], row['Y2'])
            ]
        ),
        axis=1
    )
    
    
    # Create GeoDataFrame for lines (lines only)
    gdf_line = gpd.GeoDataFrame(
        df_local, geometry='geometry_line'
    )
    # Add a column to distinguish geometry type    
    gdf_line['geometry_type'] = 'line'  
    
   
    # Save as a single GeoPackage file (supports mixed geometries)    
    gdf_line = gdf_line.rename(
        columns={'geometry_line': 'geometry'}
    ).set_geometry('geometry')
    gdf_line = gdf_line.set_crs(f'EPSG:{config["epsg"]}')
    gdf_line.to_file(gpkg_path, layer='drift_lines', driver='GPKG')
    

    # embed .qml outlier layer style
    _embed_qml_style(gpkg_path, 'drift_lines', config)
    
    # log activity
    logger = logging.getLogger('sar_drift_converter')
    logger.info(f'Created GeoPackage {gpkg_path}')
           
    
def create_plotly_html(df, html_path, config):
    """
    Create an interactive Plotly map of sea-ice drift vectors from a DataFrame.

    Renders each drift vector as a colored line segment on a stereographic
    polar projection, with start and end points marked separately. Line color
    encodes drift speed via the Viridis colorscale. The map is written to a
    self-contained HTML file using a CDN-hosted Plotly bundle.

    Args:
        df (pandas.DataFrame): Input drift observations. Expected columns:
                - 'longitude_1', 'latitude_1' (float): Start position
                                                        (EPSG:4326, degrees).
                - 'longitude_2', 'latitude_2' (float): End position
                                                        (EPSG:4326, degrees).
                - 'sea_ice_x_displacement' (float): X displacement (m);
                  combined with `sea_ice_y_displacement` to compute speed
                  magnitude for colorscale normalization.
                - 'sea_ice_y_displacement' (float): Y displacement (m).
                - 'duration_s' (float): Observation duration (s); used to
                  convert displacement magnitude to m day⁻¹.
                - 'direction_of_sea_ice_displacement' (float): Forward azimuth
                  (degrees); shown in end-point hover text.
                - 'sensor1', 'sensor2' (str): Satellite identifiers; shown
                  in end-point hover text.
                - 'outlier_category' (str): Two-digit outlier code; required
                  for level '03', where only rows with values '00' or '01'
                  are retained before plotting.
        html_path (str): Full path for the output HTML file.
        config (dict): Configuration dictionary. Must include:
                - 'level' (str): Processing level; if '03', only inlier
                  vectors (`outlier_category` in ['00', '01']) are plotted.
    
    Returns:
        None
        
    Notes:
        - Speed magnitude is computed as the Euclidean norm of
          (`sea_ice_x_displacement`, `sea_ice_y_displacement`) divided by
          `duration_s`, scaled to m day⁻¹.
        - Line colors are sampled from the Viridis colorscale using
          per-vector min-max normalized magnitude. An invisible trace with
          a colorbar is added separately so the scale renders correctly.
        - Start points are plotted in green; end points in red with hover
          text showing speed, bearing, coordinates, and sensor identifiers.
        - The map uses a stereographic projection centred at 90°N, with
          the latitude axis constrained to 60°–90°N.
        - The map title is derived from the stem of `html_path`.
        - The HTML file is written with ``include_plotlyjs='cdn'``, so an
          internet connection is required to view the output.
    """
    
    import os
    import numpy as np
    import plotly.graph_objects as go

    SECONDS_PER_DAY = 86_400
    
    
    # For level 03, retain only inlier vectors (outlier_category 00 or 01),
    # then recode to -1 to signal that outlier filtering has been applied.
    if config['level'] == '03':
        outlier_filter = df['outlier_category'].isin(['00', '01'])
        df = df[outlier_filter].copy()
        if df.shape[0] == 0:
            # it might be possible the data frame was labelled
            # as all outliers.
            return None

    mag = np.hypot(
        df['sea_ice_x_displacement'],
        df['sea_ice_y_displacement']
    ) / df['duration_s'] * SECONDS_PER_DAY


    # normalize mag to 0-1 for colorscale lookup
    mag_min, mag_max = np.nanmin(mag), np.nanmax(mag)
    mag_norm = (mag - mag_min) / (mag_max - mag_min + 1e-9)

    # sample viridis colorscale
    import plotly.colors as pc
    def mag_to_color(val):
        return pc.sample_colorscale('Viridis', val)[0]

    fig = go.Figure()

    # one trace per vector, colored by speed
    vectors = zip(
        df['longitude_1'], df['latitude_1'],
        df['longitude_2'], df['latitude_2'],
        mag, mag_norm
    )
    for i, (lon1, lat1, lon2, lat2, m, mn) in enumerate(vectors):
        fig.add_trace(go.Scattergeo(
            lon=[lon1, lon2],
            lat=[lat1, lat2],
            mode='lines',
            line=dict(width=1.5, color=mag_to_color(mn)),
            hoverinfo='skip',
            showlegend=False
        ))

        
    # start points - green
    fig.add_trace(go.Scattergeo(
        lon=df['longitude_1'],
        lat=df['latitude_1'],
        mode='markers',
        marker=dict(size=4, color='green', symbol='circle'),
        hoverinfo='skip',
        name='Start points'
    ))
    
    
    # end points - red
    fig.add_trace(go.Scattergeo(
        lon=df['longitude_2'],
        lat=df['latitude_2'],
        mode='markers',
        marker=dict(size=4, color='red', symbol='circle'),
        text=[
            f'Speed: {m:.1f} m/day<br>'
            f'Bearing: {b:.0f}°<br>'
            f'Lon: {lo:.4f}  Lat: {la:.4f}<br>'
            f'Sat: {s1}/{s2}'
            for m, b, lo, la, s1, s2 in zip(
                mag,
                df['direction_of_sea_ice_displacement'],
                df['longitude_2'], df['latitude_2'],
                df['sensor1'], df['sensor2']
            )
        ],
        hoverinfo='text',
        name='End points'
    ))        


    # invisible trace just for the colorbar
    fig.add_trace(go.Scattergeo(
        lon=df['longitude_2'],
        lat=df['latitude_2'],
        mode='markers',
        marker=dict(
            size=4,
            opacity=0,
            color=mag,
            colorscale='Viridis',
            colorbar=dict(title='Speed (m/day)', thickness=15, len=0.5),
            showscale=True
        ),
        hoverinfo='skip',
        showlegend=False
    ))


    basename = os.path.splitext(os.path.basename(html_path))[0]
    fig.update_layout(
        title=dict(
            text=(
                f'Sea-ice Drift Vectors — {basename}<br>'
                f'<sup>Observations: {len(df)} | EPSG:4326</sup>'
            ),
            x=0.5
        ),
        geo=dict(
            projection_type='stereographic',
            projection_rotation=dict(lat=90, lon=0),
            center=dict(lat=75, lon=0),
            showland=True, landcolor='lightgray',
            showocean=True, oceancolor='aliceblue',
            showcoastlines=True, coastlinecolor='black',
            lataxis=dict(range=[60, 90]),
            projection_scale=1.0,  # lower = more zoomed out, adjust to taste
        ),
        dragmode='zoom',
        width=2000,
        height=2000
    )

    fig.write_html(html_path, include_plotlyjs='cdn')

    import logging
    logging.getLogger('sar_drift').info(f'Created Plotly HTML {html_path}')
    
    
def combine_daily_netcdf_files(config, nc_files, template_ds,
                               daily_start_date, daily_end_date,
                               daily_nc_path, multi_layered=True,
                               overwrite=False):
    """
    Combine multiple sliced SAR drift NetCDF files into one full daily mosaic
    on the template grid.

    Reads each per-scene NetCDF file produced by `create_netcdf`, merges all
    variables onto a shared daily grid, and writes the result to a single
    output NetCDF file. Supports both multi-layered output (one time layer
    per scene) and single-layer output (scenes mosaicked into one time slice).
    Projection metadata is sourced entirely from the CDL template specified
    in `config`.

    Args:
        config (dict): Configuration dictionary. Must include:
            - 'netcdf_cdl_file' (str): Path to the CDL template file whose
              `spatial_ref` variable defines the output projection. Set this
              to the CDL file matching the target EPSG (e.g.
              `sar_drift_output_3413.cdl` or `sar_drift_output_6931.cdl`).
            - 'level' (str): Processing level; used to determine whether to
              write a cell-update log (`'00'` only).
            - 'output_dir' (str): Directory where `cell_update_log.csv` is
              written when `config['level'] == '00'` and overlapping cells
              are detected.
        nc_files (list[str]): Paths to per-scene sliced NetCDF files to
            merge, as produced by `create_netcdf`.
        template_ds (xarray.Dataset): Template dataset providing the target
            grid coordinate arrays (`x`, `y`) and grid dimensions. Must
            share the same projection and coordinate spacing as the input
            scene files.
        daily_start_date (str): Start date of the daily mosaic in `YYYYMMDD`
            format; used to set `time_coverage_start` global attribute.
        daily_end_date (str): End date of the daily mosaic in `YYYYMMDD`
            format; used to set `time_coverage_end` global attribute.
        daily_nc_path (str): Full path for the output daily NetCDF file.
        multi_layered (bool): If `True` (default), each scene is written as
            a separate time layer. If `False`, all scenes are mosaicked into
            a single time slice using a last-write-wins strategy controlled
            by `overwrite`.
        overwrite (bool): Controls single-layer conflict resolution when
            `multi_layered=False`. If `False` (default), the first valid
            (non-NaN) value written to a cell is kept. If `True`, later
            scenes overwrite earlier ones based on scene timestamp.

    Returns:
        None. The output file is written to `daily_nc_path`. When
        `multi_layered=False` and `config['level'] == '00'`, a
        `cell_update_log.csv` is also written to `config['output_dir']`
        recording any cells where an earlier value was overwritten.

    Notes:
        - Output projection is fully determined by the CDL template referenced
          in `config['netcdf_cdl_file']`. No EPSG is hardcoded in this
          function; switching projection requires only pointing `config` at
          the appropriate CDL file.
        - Scene files are sorted by their `time` coordinate value before
          merging, ensuring consistent ordering regardless of input list order.
        - For single-layer mode, `latest_time_grid` tracks the timestamp of
          the last write per cell to enforce the `overwrite` policy.
        - `time_bnds` spans `[min(scene_start), max(scene_end)]` across all
          merged scenes for single-layer output, and per-scene bounds for
          multi-layered output.
        - All int16 flag variables (`outlier_category`, `bearing_error`,
          `speed_error`, `measurement_error`) use −9 as their `_FillValue`.
        - The dataset is always closed in the `finally` block even if an
          error occurs during merging or writing.
    """

    import numpy as np
    import pandas as pd
    import xarray as xr
    from datetime import datetime

    # template grid settings
    x_coords = template_ds["x"].values
    y_coords = template_ds["y"].values

    # time defaults for output daily file
    min_time = pd.Timestamp(daily_start_date)
    max_time = pd.Timestamp(daily_end_date)

    if multi_layered:
        n_time = len(nc_files)
    else:
        n_time = 1

    # finalize grid shape
    grid_shape = (n_time, template_ds.sizes["y"], template_ds.sizes["x"])

    # track last_write time per cell (single-layer only)
    latest_time_grid = np.full(
        (template_ds.sizes["y"], template_ds.sizes["x"]),
        -np.inf,
        dtype=np.float64
    )

    # variables to merge spatially
    var_names = [
        "sea_ice_speed",
        "sea_ice_x_displacement",
        "sea_ice_y_displacement",
        "direction_of_sea_ice_displacement",
        "outlier_category",
        "bearing_error",
        "speed_error",
        "measurement_error"
    ]

    daily_grid = None
    time_list = []
    update_log = []
    layer_id_list = []

    try:
        # build output dataset from CDL metadata
        meta_ds = _set_metadata(config)

        global_attrs = meta_ds.attrs.copy()
        sea_ice_speed_attrs = meta_ds["sea_ice_speed"].attrs.copy()
        sea_ice_x_attrs = meta_ds["sea_ice_x_displacement"].attrs.copy()
        sea_ice_y_attrs = meta_ds["sea_ice_y_displacement"].attrs.copy()
        direction_attrs = (
            meta_ds["direction_of_sea_ice_displacement"].attrs.copy()
        )
        outlier_attrs = meta_ds["outlier_category"].attrs.copy()
        bearing_error_attrs = meta_ds["bearing_error"].attrs.copy()
        speed_error_attrs = meta_ds["speed_error"].attrs.copy()
        measurement_error_attrs = meta_ds["measurement_error"].attrs.copy()
        spatial_ref_attrs = meta_ds["spatial_ref"].attrs.copy()
        x_attrs = meta_ds["x"].attrs.copy()
        y_attrs = meta_ds["y"].attrs.copy()
        time_attrs = meta_ds["time"].attrs.copy()
        layer_id_attrs = meta_ds["layer_id"].attrs.copy()
        time_attrs['coordinates'] = 'layer_id'

        meta_ds.close()
        del meta_ds

        # placeholder time and bounds — updated after merge loop
        time_array = np.zeros(n_time, dtype='float64')
        time_bounds = np.zeros((n_time, 2), dtype='float64')

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
                "bearing_error": (
                    ("time", "y", "x"),
                    np.full(grid_shape, -9, dtype=np.int16),
                    bearing_error_attrs,
                ),
                "speed_error": (
                    ("time", "y", "x"),
                    np.full(grid_shape, -9, dtype=np.int16),
                    speed_error_attrs,
                ),
                "measurement_error": (
                    ("time", "y", "x"),
                    np.full(grid_shape, -9, dtype=np.int16),
                    measurement_error_attrs,
                ),
                "spatial_ref": (
                    (),
                    np.int32(0),
                    spatial_ref_attrs,
                ),
                "time_bnds": (
                    ("time", "nv"),
                    time_bounds,
                ),
            },
            coords={
                "time": ("time", time_array, time_attrs),
                "nv": [0, 1],
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

        # sort scene files by time
        file_times = []
        for nc_file in nc_files:
            with xr.open_dataset(
                nc_file, decode_times=False, mask_and_scale=False
            ) as scene_ds:
                file_times.append(
                    (float(scene_ds['time'].values[0]), nc_file)
                )
        file_times.sort(key=lambda x: x[0])


        # merge each scene into the daily grid
        for nc_idx, (scene_time, nc_file) in enumerate(file_times):
            with xr.open_dataset(
                nc_file, decode_times=False, mask_and_scale=False
            ) as scene_ds:

                scene_x = scene_ds['x'].values
                scene_y = scene_ds['y'].values
                t_idx = nc_idx if multi_layered else 0

                # read scene time bounds from its time_bnds variable
                scene_bnds = scene_ds['time_bnds'].values  # shape (1, 2)
                scene_start = float(scene_bnds[0, 0])
                scene_end = float(scene_bnds[0, 1])

                if multi_layered:
                    # each scene gets its own time layer
                    time_list.append(float(scene_ds['time'].values[0]))
                    time_bounds[t_idx, 0] = scene_start
                    time_bounds[t_idx, 1] = scene_end
                    if 'layer_id' in scene_ds.coords or \
                            'layer_id' in scene_ds:
                        layer_id_list.append(
                            str(scene_ds['layer_id'].values[0])
                        )
                    else:
                        layer_id_list.append('')
                else:
                    # single layer: keep earliest start, latest end
                    if time_bounds[0, 0] == 0 or \
                    scene_start < time_bounds[0, 0]:
                        time_bounds[0, 0] = scene_start
                    if scene_end > time_bounds[0, 1]:
                        time_bounds[0, 1] = scene_end

                # get x/y placement indices on template grid
                x_start = int(np.where(x_coords == scene_x[0])[0][0])
                x_end   = int(np.where(x_coords == scene_x[-1])[0][0])
                y_start = int(np.where(y_coords == scene_y[0])[0][0])
                y_end   = int(np.where(y_coords == scene_y[-1])[0][0])

                x_0, x_1 = min(x_start, x_end), max(x_start, x_end)
                y_0, y_1 = min(y_start, y_end), max(y_start, y_end)

                if multi_layered:
                    for var_name in var_names:
                        scene_vals = scene_ds[var_name].isel(time=0).values
                        daily_grid[var_name].values[
                            t_idx, y_0:y_1+1, x_0:x_1+1
                        ] = scene_vals
                else:
                    ref_vals = scene_ds[var_names[0]].isel(time=0).values
                    last_t = latest_time_grid[y_0:y_1+1, x_0:x_1+1]
                    valid = np.isfinite(ref_vals)
                    newer = scene_time > last_t
                    write_mask = valid & newer

                    if write_mask.any():
                        local_rows, local_cols = np.where(write_mask)
                        for lr, lc in zip(local_rows, local_cols):
                            old_ts = last_t[lr, lc]
                            update_log.append({
                                "i":             y_0 + lr,
                                "j":             x_0 + lc,
                                "old_timestamp": old_ts,
                                "new_timestamp": scene_time,
                                "nc_file":       nc_file,
                                "overwrite":     old_ts != -np.inf
                            })

                        for var_name in var_names:
                            scene_vals = scene_ds[var_name].isel(time=0).values
                            target = daily_grid[var_name].values[
                                0, y_0:y_1+1, x_0:x_1+1
                            ]
                            target[write_mask] = scene_vals[write_mask]
                            daily_grid[var_name].values[
                                0, y_0:y_1+1, x_0:x_1+1
                            ] = target

                        latest_time_grid[
                            y_0:y_1+1, x_0:x_1+1
                        ][write_mask] = scene_time


        # Update time coordinate and bounds after merge
        if multi_layered:
            final_time_array = np.array(time_list, dtype='float64')
        else:
            # use scene start (first bound) as the time coordinate
            final_time_array = np.array([time_bounds[0, 0]], dtype='float64')

        daily_grid = daily_grid.assign_coords(
            time=('time', final_time_array, daily_grid['time'].attrs)
        )
        # write populated time_bounds into the dataset
        daily_grid['time_bnds'].values[:] = time_bounds

        # assign layer_id coordinate (multi-layered only)
        if multi_layered and layer_id_list:
            daily_grid = daily_grid.assign_coords(
                layer_id=('time', np.array(layer_id_list), layer_id_attrs)
            )

        # pop _FillValue from int16 variable attrs before writing
        for var in [
                'outlier_category', 'bearing_error',
                'speed_error', 'measurement_error'
            ]:
            daily_grid[var].attrs.pop('_FillValue', None)
            daily_grid[var].encoding['_FillValue'] = np.int16(-9)
            daily_grid[var].encoding['dtype'] = np.int16


        # Save to NetCDF
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
                "bearing_error": {
                    "zlib": True, "complevel": 4, "dtype": "int16",
                    "_FillValue": np.int16(-9)
                },
                "speed_error": {
                    "zlib": True, "complevel": 4, "dtype": "int16",
                    "_FillValue": np.int16(-9)
                },
                "measurement_error": {
                    "zlib": True, "complevel": 4, "dtype": "int16",
                    "_FillValue": np.int16(-9)
                },
                "time_bnds": {"dtype": "float64"},
                "spatial_ref": {"dtype": "int32"},
            }
        )

        if update_log and config['level'] == '00':
            update_df = pd.DataFrame(update_log)
            df_filter = update_df['overwrite']
            update_df = update_df[df_filter].drop(columns='overwrite')
            update_df = update_df.sort_values(['i', 'j'])
            log_path = os.path.join(config['output_dir'], 'cell_update_log.csv')
            update_df.to_csv(log_path, index=False)

    finally:
        if daily_grid is not None:
            daily_grid.close()
            del daily_grid


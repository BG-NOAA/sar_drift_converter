# -*- coding: utf-8 -*-
"""
******************************************************************************

 Project:    SAR Drift Output Generator
 Purpose:    Utility functions for sar_drift_output
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

from pyproj import CRS, Transformer, Geod

from typing import Tuple

#=========================
# Standard error messaging
#=========================

def error_msg(msg, rc):
    """
    Print an error message with a warning icon and exit the program.

    Parameters
    ----------
    msg : str
        The error message to display in the console.

    rc : int
        The return code with which to exit the script.

    Notes
    -----
    - The message is prefixed with a warning symbol (⚠️).
    - This function immediately terminates the program using `exit(rc)`.
    """

    
    print(f"  ⚠️ {msg}")
    exit(rc)
    
    
#===================
# Internal functions
#===================

def _set_transformer():
    transformer = {}
    
    # CRS setup
    transformer['epsg'] = 3413
    transformer['crs_string_3413'] = CRS.from_string(
        "+proj=stere +lat_0=90 +lat_ts=70 +lon_0=-45 "
        "+x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs +type=crs"
    )
    transformer['crs_string_4326'] = CRS.from_string(
        "+proj=longlat +datum=WGS84 +no_defs +type=crs"
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
    
    transformer['4326_3413'] = Transformer.from_crs(
        transformer['crs_string_4326'],
        transformer['crs_string_3413'],
        always_xy=True
    )

    transformer['3413_4326'] = Transformer.from_crs(
        transformer['crs_string_3413'],
        transformer['crs_string_4326'],
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
    if config['verbose']:
        print(f'  {myCmd1}')
        print(f'  ncgen return code: {rc}')
    
    if rc != 0:
        error_msg('Error in `ncgen` call. Cannot continue.', 16)
        
    return xr.open_dataset(ncgen_ofile_nc, decode_times=False)


def _parse_pair_times(name):
    import re
    from datetime import datetime
    
    DT_RE = re.compile(r"(\d{4}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2})")
    parts = DT_RE.findall(name)
    if len(parts) < 2:
        raise ValueError(f"Expected 2 timestamps, found {len(parts)} in: {name}")
    t1 = datetime.strptime(parts[0], "%Y_%m_%d_%H_%M_%S")
    t2 = datetime.strptime(parts[1], "%Y_%m_%d_%H_%M_%S")
    return t1, t2


#=========
# Data I/O
#=========

def read_sar_drift_data_file(input_file, config):
    """
    Load and preprocess SAR drift data from a CSV file.

    This function performs the following:
        - Reads a SAR drift CSV file with start/end positions and times
        - Cleans the dataset by removing invalid records
        - Converts time values (Julian seconds since 2000-01-01) to 
          readable timestamps
        - Computes observation durations in both datetime and seconds
        - Rounds and converts lat/lon coordinates to a specified decimal
          precision
        - Projects coordinates from WGS84 to EPSG:3413 using a pyproj
          Transformer
        - Computes zonal (dx) and meridional (dy) displacements in meters
        - Converts U/V velocity from m/s to km/day
        - Calculates total drift distance in kilometers using projected
          coordinates
        - Writes a formatted intermediate CSV to the output directory

    Returns:
        pandas.DataFrame: Cleaned and enriched DataFrame with
        added columns:
            - Date1, Date2: Human-readable timestamps
            - Duration, JS_Duration: Observation durations
            - Lon1, Lat1, Lon2, Lat2: Rounded geographic coordinates
            - X1, Y1, X2, Y2: Projected coordinates (EPSG:3413, meters)
            - dx, dy: Displacements (meters)
            - U_kmdy, V_kmdy: Velocities in km/day
            - total_distance_km: Great-circle distance in kilometers
    """
    import pandas as pd
    import numpy as np
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
    
    precision = config['precision']
    
    # Read the SAR drift data file
    df = pd.read_csv(
        input_file, delimiter=config['delimiter'],
        header=0, engine='c', skiprows=config['skip_rows_before_header']
    )
    df.columns = df.columns.str.strip()
    
    
    # Add the appropriate input file to a data frame
    # Julian seconds start from date 01-01-2000
    base_time = datetime(2000, 1, 1)

    # Remove rows from Data Frame where orig_bearing = 0
    # The values for these observations are incorrect
    df = df[df['Bear_deg'] != 0]

    # Create new Date* columnc by converting Time_JS* columns to datetime
    df['Date1'] = df["Time1_JS"].apply(
        lambda x: base_time + timedelta(seconds=x)
        )
    df['Date1'] = df['Date1'].dt.strftime('%Y-%m-%d %H:%M:%S')
    df['Date2'] = df["Time2_JS"].apply(
        lambda x: base_time + timedelta(seconds=x)
        )
    df['Date2'] = df['Date2'].dt.strftime('%Y-%m-%d %H:%M:%S')


    # Calculate duration of observations
    # 1. Date time
    # 2. Raw Julian seconds
    df['Duration'] = pd.to_timedelta(
        df['Time2_JS'] - df['Time1_JS'], unit='s'
        ).astype(str)
    df['JS_Duration'] = (
        df['Time2_JS'] - df['Time1_JS']
        )


    # Convert lon/lat to float and round
    df['Lon1'] = np.round(df['Lon1'].astype(float), precision)
    df['Lat1'] = np.round(df['Lat1'].astype(float), precision)
    df['Lon2'] = np.round(df['Lon2'].astype(float), precision)
    df['Lat2'] = np.round(df['Lat2'].astype(float), precision)
    

    # transform lon/lat to polarstereographic meters
    transformer = _set_transformer()
    
    df['X1'], df['Y1'] = transformer['4326_3413'].transform(
        df['Lon1'].values, df['Lat1'].values
    )
    df['X2'], df['Y2'] = transformer['4326_3413'].transform(
        df['Lon2'].values, df['Lat2'].values
    )
    
    # Get the zonal and meridional displacment used by NetCDF
    df['U_kmdy'] = (df['U_vel_ms'] * 60 * 60 * 24) / 1000 # in km
    df['V_kmdy'] = (df['V_vel_ms'] * 60 * 60 * 24) / 1000 # in km
    

    # set dX and dY to plot quivers
    df['dx'] = df['X2'] - df['X1']
    df['dy'] = df['Y2'] - df['Y1']
    df['total_distance_km'] = compute_distance_meters(
        df['X1'].values, df['Y1'].values,
        df['X2'].values, df['Y2'].values,
        precision
    )
    
    
    df['Sat1'] = df["File1"].str.partition("_")[0]
    df['Sat2'] = df["File2"].str.partition("_")[0]
    
    return df


def create_shape_package(df, base_name, config):
    """
    Generate a GeoPackage (.gpkg) file with point and line geometries
    derived from SAR drift data, suitable for visualization in GIS software.

    This function processes a SAR drift DataFrame and performs the following:
        - Transforms geographic coordinates (lon/lat) to Polar Stereographic
          (EPSG:3413)
        - Creates start and end point geometries for each drift vector
        - Creates line geometries connecting start and end points
        - Saves all geometries into a single multi-layer GeoPackage file with
          three layers: 'start_points', 'end_points', and 'drift_lines'

    Each output layer:
        - Uses the EPSG:3413 coordinate reference system
        - Includes the original date and position metadata
        - Can be opened in GIS software such as QGIS

    Parameters:
        config (dict): Dictionary of user-defined arguments, including:
            - 'output_dir' (str): Path to the directory for saving
                                  the .gpkg file
            - sar_drift_file_base: Basename by which to name the output files
            - transformer (pyproj.Transformer): Transformer to convert WGS84
                                                to EPSG:3413
        df (pandas.DataFrame): DataFrame containing SAR drift data, including:
            - 'Date1', 'Date2': Observation timestamps
            - 'Lon1', 'Lat1', 'Lon2', 'Lat2': Geographic coordinates

    Returns:
        tuple:
            gdf_start (geopandas.GeoDataFrame): GeoDataFrame of start point
                                                geometries 
                (EPSG:3413) including metadata fields and 'geometry_type' =
                'point'.
            gdf_line (geopandas.GeoDataFrame): GeoDataFrame of drift line
                                               geometries connecting start and
                                               end points, with 'geometry_type'
                                               = 'line'.

    Output:
        Writes a GeoPackage file named "sar_drift_<timestamp>.gpkg"
        with three layers:
            - 'start_points': Point geometries at drift start locations
            - 'end_points': Point geometries at drift end locations
            - 'drift_lines': Line geometries connecting start to end

    Notes:
        - All geometries are tagged with a 'geometry_type' field
          ('point' or 'line')
        - Geometry is projected in meters (EPSG:3413)
        - Useful for visualizing individual drifts or overlaying
          with SAR data in GIS
    """

    import os
    import pandas as pd
    import geopandas as gpd
    from shapely.geometry import Point, LineString
    
    # reduce data frame to needed features
    df_local = df.copy()
    transformer = _set_transformer()
    
    # transform projection
    df_local['X1'], df_local['Y1'] = transformer['4326_3413'].transform(
        df_local['Lon1'].values, df_local['Lat1'].values
    )
    df_local['X2'], df_local['Y2'] = transformer['4326_3413'].transform(
        df_local['Lon2'].values, df_local['Lat2'].values
    )

    # Create Point and Line Geometries
    df_local['geometry_start'] = df_local.apply(
        lambda row: Point((row['X1'], row['Y1'])), axis=1
    )
    
    df_local['geometry_end'] = df_local.apply(
        lambda row: Point((row['X2'], row['Y2'])), axis=1
    )
    df_local['geometry_line'] = df_local.apply(
        lambda row: LineString(
            [(row['X1'], row['Y1']), (row['X2'], row['Y2'])]
        ),
        axis=1
    )

    # Create GeoDataFrame for start points (points only)
    gdf_start = gpd.GeoDataFrame(
        df_local, geometry='geometry_start'
    )
    # Add a column to distinguish geometry type    
    gdf_start['geometry_type'] = 'point'  
    
    # Create GeoDataFrame for end points (points only)
    gdf_end = gpd.GeoDataFrame(
        df_local, geometry='geometry_end'
    )
    # Add a column to distinguish geometry type    
    gdf_end['geometry_type'] = 'point'  
    
    # Create GeoDataFrame for lines (lines only)
    gdf_line = gpd.GeoDataFrame(
        df_local, geometry='geometry_line'
    )
    # Add a column to distinguish geometry type    
    gdf_line['geometry_type'] = 'line'  
    
    # Combine the two GeoDataFrames while retaining original fields
    gdf_combined = pd.concat([
        gdf_start.rename(columns={'geometry_start': 'geometry'}),
        gdf_end.rename(columns={'geometry_end': 'geometry'}),
        gdf_line.rename(columns={'geometry_line': 'geometry'})
    ], ignore_index=True)
    
    # Recreate the GeoDataFrame with the common geometry column
    gdf_combined = gpd.GeoDataFrame(
        gdf_combined, geometry='geometry'
    )
    
    # Save as a single GeoPackage file (supports mixed geometries)
    geopackage_file = f"{base_name}.gpkg"
    output_file_path = os.path.join(
        config['output_dir'], f"{geopackage_file}"
    )
    
    gdf_start = gdf_start.rename(
        columns={'geometry_start': 'geometry'}
    ).set_geometry('geometry')
    gdf_start.crs = CRS.from_epsg(transformer['epsg'])
    gdf_start.to_file(output_file_path, layer='start_points', driver='GPKG')
    
    gdf_end = gdf_end.rename(
        columns={'geometry_end': 'geometry'}
    ).set_geometry('geometry')
    gdf_end.crs = CRS.from_epsg(transformer['epsg'])
    gdf_end.to_file(output_file_path, layer='end_points', driver='GPKG')
    
    
    gdf_line = gdf_line.rename(
        columns={'geometry_line': 'geometry'}
    ).set_geometry('geometry')
    gdf_line.crs = CRS.from_epsg(transformer['epsg'])
    gdf_line.to_file(output_file_path, layer='drift_lines', driver='GPKG')
    
    gdf_start = gdf_start['geometry']
    gdf_line = gdf_line['geometry']
    
    if config['verbose']:
        print("  GeoPackage created")
    
    return gdf_start, gdf_line


def create_netcdf(df, base_name, config):
    """
    Generate a CF/ACDD-compliant NetCDF file from SAR drift data.

    This function performs the following operations:
        - Projects geographic coordinates (longitude/latitude) into 
          EPSG:3413 (Polar Stereographic) using a pyproj Transformer
        - Defines a 2D spatial grid at 1 km resolution based on the spatial
          extent of the drift data
        - Initializes NetCDF variables for:
              - `Speed_kmdy` (drift speed in km/day)
              - `dx`, `dy` (zonal/meridional displacement in meters/day)
              - `Bear_deg` (bearing in degrees from true north)
        - Computes the observation time range and stores it as a CF-compliant
          time coordinate (seconds since Unix epoch)
        - Loads metadata from a CDL file and populates standard global 
          attributes in the NetCDF file
        - Maps each drift observation to the nearest grid cell, 
          skipping duplicates with a warning
        - Writes the result to a compressed `.nc` file (NetCDF4 format)

    Parameters:
        config (dict): Dictionary containing script arguments, including:
            - 'input_filename': Path to the SAR drift input file
            - 'netcdf_cdl_file': Path to CDL file containing NetCDF metadta
                                 standards
            - 'output_dir': Path to directory save NetCDF file
            - 'sar_drift_file_basename': Basename by which to name the
                                         output files
            - 'transformer' (pyproj.Transformer): Transformer to convert WGS84
                                                to EPSG:3413
        df (pandas.DataFrame): Cleaned SAR drift data containing the
                               following fields:
            - 'X1', 'Y1', 'X2', 'Y2': Projected coordinates in meters
              (EPSG:3413)
            - 'dx', 'dy': Displacements in meters/day
            - 'Speed_kmdy': Speed in kilometers per day
            - 'Bear_deg': Bearing angle in degrees
            - 'Date1': Observation datetime string 
                      (used to extract time coverage)
        transformer (pyproj.Transformer): Transformer used for coordinate
                                          projection
        timestamp (str): Timestamp string used to name the output NetCDF file
        cdl_file (str): Name of the file with the NetCDF metadata standards

    Returns:
        None

    Output:
        Writes a NetCDF file named `sar_drift_<timestamp>.nc` to the
        `output/` directory.

    Notes:
        - The grid is defined in projected meters (EPSG:3413) with 1 km
          resolution
        - Metadata placeholders in the CDL template (e.g., `FILL_DATE_CREATED`)
          are replaced with actual values at runtime
        - Observations mapped to the same grid cell will emit a warning
          and be skipped
        - The resulting NetCDF is compatible with QGIS and other
          CF-compliant tools
    """

    import os
    import numpy as np
    import pandas as pd
    from datetime import datetime
    import xarray as xr
   
    # Define grid resolution and bounds
    resolution_km = 1  # Resolution in km
    

    # reduce data frame to needed features   
    cols = [
        'Date1', 'X1', 'Y1', 'X2', 'Y2', 'dx', 'dy', 'Speed_kmdy', 'Bear_deg'
    ]
    df_reduced = df[cols].copy()
    df_reduced['Date1'] = pd.to_datetime(df_reduced['Date1'])
    
    
    # Get the absolute minimum and maximum for lat (Y) and lon (X)
    min_x, max_x = (
        df_reduced[['X1', 'X2']].min().min(),
        df_reduced[['X1', 'X2']].max().max()
    )
    min_y, max_y = (
        df_reduced[['Y1', 'Y2']].min().min(),
        df_reduced[['Y1', 'Y2']].max().max()
    )
    
    
    # Build the X and Y coordinates based on maximum and minimum
    # with steps of resolution multiplied by 1000 km
    x_coords = np.arange(min_x, max_x, resolution_km * 1000)
    y_coords = np.arange(min_y, max_y, resolution_km * 1000)
    
    try:
        # Create an empty grid
        # (time, y, x)
        grid_shape = (1, len(y_coords), len(x_coords))  
        
        # time defaults
        epoch = datetime(1970, 1, 1)
        mean_time = df_reduced['Date1'].mean()
        min_time = df_reduced['Date1'].min()
        max_time = df_reduced['Date1'].max()
        
        # convert to "seconds since 1970-01-01 00:00:00"
        time_sec = (mean_time - epoch).total_seconds()
        
        # time array for NetCDF
        time_array = np.array([time_sec], dtype='float64')
        
        # shell of NetCDF
        netcdf_grid = xr.Dataset(
            {
                'Speed_kmdy': (('time', 'y', 'x'),
                                np.full(grid_shape, np.nan),
                                {
                                    'long_name': "Speed in km/day",
                            		'standard_name': "sea_ice_speed",
                                    'ioos_category': (
                                        "SAR daily sea-ice drift"
                                        ),
                                    'units': "km/day",
                                    'grid_mapping': "spatial_ref"
                                    }
                                ),
                'dx': (('time', 'y', 'x'),
                              np.full(grid_shape, np.nan),
                              {
                                  'long_name': 'Zonal Velocity',
                                  'standard_name': 'movement_in_x_direction',
                                  'ioos_category': 'SAR daily sea-ice drift',
                                  'units': 'm/day',
                                  'grid_mapping': 'spatial_ref'
                                  }
                              ),
                'dy': (('time', 'y', 'x'),
                              np.full(grid_shape, np.nan),
                              {
                                  'long_name': 'Meridional Velocity',
                                  'standard_name': 'movement_in_y_direction',
                                  'ioos_category': 'SAR daily sea-ice drift',
                                  'units': 'm/day',
                                  'grid_mapping': 'spatial_ref'
                                  }
                              ),
                'Bear_deg': (('time', 'y', 'x'),
                              np.full(grid_shape, np.nan),
                              {
                                  'long_name': 'Bearing',
                                  'standard_name': "direction_true_north",
                                  'ioos_category': 'SAR daily sea-ice drift',
                                  'units': 'degrees',
                                  'grid_mapping': 'spatial_ref'
                                  }
                              )               
            },
            # Add metadata to coords so QGIS can properly scale the map
            coords={
                'x': (('x',), x_coords,
                      {
                          'actual_range': (
                              [float(x_coords.min()), float(x_coords.max())]
                              ),
                          'axis': 'X',
                          'comment': (
                              'x values are the centers of the grid cells'
                              ),
                          'ioos_category': 'Location',
                          'long_name': 'x coordinate of projection',
                          'standard_name': 'projection_x_coordinate',
                          'units': 'm'
                          }),
                'y': (('y',), y_coords,
                      {
                          'actual_range': (
                              [float(y_coords.min()), float(y_coords.max())]
                              ),
                          'axis': 'Y',
                          'comment': (
                              'y values are the centers of the grid cells'
                              ),                          
                          'ioos_category': 'Location',
                          'long_name': 'y coordinate of projection',
                          'standard_name': 'projection_x_coordinate',
                          'units': 'm'
                          }),
                'time': (('time',), time_array, {
                    'actual_range': (
                        [float(time_array.min()), float(time_array.max())]
                        ),
                    'axis': 'T',
                    'comment': (
                        'This is the 00Z reference time. '
                        'Note that products are nowcasted to be valid '
                        'specifically at the time given here.'
                        ),
                    'CoordinateAxisType': 'Time',
                    'ioos_category': 'Time',
                    'long_name': 'Centered Time',
                    'standard_name': 'time',
                    'time_origin': '01-Jan-1970 0:00:00',
                    'units': "seconds since 1970-01-01 00:00:00 UTC"
                })
            }
        )
        
        
        # Set NetCDF standard attributes
        metadata_nc = _set_metadata(config)
        
        
        # Replace placeholders with real values
        netcdf_grid.attrs.update(metadata_nc.attrs)
        netcdf_grid.attrs['date_created'] = (
            datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
            )
        netcdf_grid.attrs['time_coverage_start'] = (
            min_time.strftime('%Y-%m-%dT%H:%M:%SZ')
            )
        netcdf_grid.attrs['time_coverage_end'] = (
            max_time.strftime('%Y-%m-%dT%H:%M:%SZ')
            )
        
        
        
        # Mapping data to the grid
        index_mapping = {}
        for _, row in df_reduced.iterrows():
            # To get the i, j indices, we
            x_idx = np.argmin(np.abs(x_coords - row['X1']))
            y_idx = np.argmin(np.abs(y_coords - row['Y1']))
                
            
            # Create a unique key for each (i, j) pair
            index_key = (y_idx, x_idx)
            
            # Check if this index already exists
            if index_key in index_mapping:
                print(f"Duplicate index detected at (i, j): {index_key}")
            else:
                # Store data in the grid
                netcdf_grid['Speed_kmdy'][0, y_idx, x_idx] = row['Speed_kmdy']
                netcdf_grid['dx'][0, y_idx, x_idx] = row['dx']
                netcdf_grid['dy'][0, y_idx, x_idx] = row['dy']
                netcdf_grid['Bear_deg'][0, y_idx, x_idx] = row['Bear_deg']
        
        
        # Save to NetCDF with compression level 4
        
        output_file_path = os.path.join(
            config['output_dir'], f"{base_name}.nc"
        )
    
        # Save to NetCDF with compression level 4
        netcdf_grid.to_netcdf(output_file_path, mode='w', encoding={
            'Speed_kmdy': {'zlib': True, 'complevel': 4},
            'dx': {'zlib': True, 'complevel': 4},
            'dy': {'zlib': True, 'complevel': 4},
            'Bear_deg': {'zlib': True, 'complevel': 4}
        })
    
        
        
        
    finally:
        # Ensure that these lines are executed even if an error occurs
        netcdf_grid.close()
        del netcdf_grid
        
        print('  NetCDF file created')
        

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
    from pyproj import Transformer
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
    

    # initialize plot
    fig = plt.figure(figsize=(18, 10))
    
    if config['create_region_plot']:
        # -------------------------------
        # left map of subplot
        # -------------------------------
        
        # --- overview map with land and coastlines---
        # transform 3413 to 4326 to draw True North arrow
        to_lonlat = Transformer.from_crs(
            "EPSG:3413", "EPSG:4326", always_xy=True
        )
        
        # Convert all 4 corners of the SAR extent
        corner_coords = [
            (xmin, ymin),
            (xmax, ymin),
            (xmax, ymax),
            (xmin, ymax),
            (xmin, ymin)  # close the loop
        ]
        
        # transform meters to degrees
        corner_lonlat = [to_lonlat.transform(x, y) for x, y in corner_coords]
        
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
    mag = np.hypot(dx, dy) / 1000  # magnitude in km
    Q = ax.quiver(
        X, Y, u, v, mag,
        angles='xy',
        scale_units='xy',
        # scale=config['quiver_scale_small_area'],
        scale=0.5,
        width=0.003,
        cmap='viridis',
        alpha=0.8
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
    ax.set_title('dX, dY Vectors with Magnitude', fontsize=12)
    fig.suptitle(
        f"Vector Overlay on GeoTiff:\n{base_name}",
        fontsize=14
    )
    
   
    # save plot as .png
    png_file = os.path.join(
        config['output_dir'], f"{base_name}.png"
    )
    fig.savefig(png_file, bbox_inches='tight', dpi=300)
    
    if config['verbose']:
        print('  Overlay plot created')
    
    
    return fig
        

def read_geotiff_rasterio(geotiff_file):
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
    
        
#=============
# Calculations
#=============

def compute_bearing(
    lat1: float,  # Starting latitude(s), can be a single float or a list of floats
    lon1: float,  # Starting longitude(s), can be a single float or a list of floats
    lat2: float,  # Ending latitude(s), can be a single float or a list of floats
    lon2: float   # Ending longitude(s), can be a single float or a list of floats
) -> Tuple[float, float]:       # Returns a tuple: (fwd_azimuth, back_azimuth, distance)

    """
    Calculate the daily drift between two points (start and end) based on their latitude and longitude.

    :param lat1: Starting latitude(s)  
    :param lon1: Starting longitude(s)  
    :param lat2: Ending latitude(s)  
    :param lon2: Ending longitude(s)  
    :return: 
        - fwd_azimuth (float): Forward azimuth in degrees (0 to 360), measured clockwise from true north
        - distance (float): Great circle distance between the two points in meters
    :ref: https://pyproj4.github.io/pyproj/stable/api/geod.html#pyproj.Geod.inv
    """

    # Initialize a geodetic object using the WGS84 ellipsoid
    geod = Geod(ellps='WGS84')

    # Calculate azimuth and distance using geod.inv method
    # Note: Arguments order is (lon1, lat1, lon2, lat2) as required by pyproj.Geod.inv
    fwd_azimuth, _ , distance = geod.inv(lon1, lat1, lon2, lat2)
    
    # Return the calculated forward azimuth, back azimuth, and distance
    return fwd_azimuth, distance 
    
    
def compute_distance_meters(x1, y1, x2, y2, precision):
    """
    Compute planar bearing (clockwise from north) and Euclidean distance
    between two points in a projected CRS (e.g., EPSG:3413).
    
    Parameters:
        x1 (float): Starting longitude
        y1 (float): Starting latitude
        x2 (float): Ending longitude
        y2 (float): Ending latitude
        precision: Round significant digits
        
    Returns:
        distance (float): Computed Euclidean distance
    """
    
    
    import numpy as np
    
    dx = x2 - x1
    dy = y2 - y1

    # Distance in kilometers --> np.hypot=(dx^2+dy^2)^.5
    distance = np.round(np.hypot(dx, dy) / 1000, precision)

    return distance
   

def circular_mean(a):
    import numpy as np
    return np.arctan2(np.nanmean(np.sin(a)), np.nanmean(np.cos(a)))


def circular_std(a):
    import numpy as np
    s = np.nanmean(np.sin(a))
    c = np.nanmean(np.cos(a))
    R = np.sqrt(s*s + c*c)
    return np.sqrt(-2 * np.log(np.clip(R, 1e-12, 1.0)))

    
#==================
# Plot enhancements
#==================

def add_graticules(ax, map_extent):
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
    from pyproj import Transformer
    
    # Transformer from EPSG:3413 to EPSG:4326
    to_lonlat = Transformer.from_crs("EPSG:3413", "EPSG:4326", always_xy=True)
    
    # Corners in degrees
    lon_min, lat_min = to_lonlat.transform(map_extent[0], map_extent[2])
    lon_max, lat_max = to_lonlat.transform(map_extent[1], map_extent[3])
    
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


    to_3413 = Transformer.from_crs("EPSG:4326", "EPSG:3413", always_xy=True)
    
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
        points = [to_3413.transform(lon, lat) for lat in lats]
        xs, ys = zip(*points)
        ax.plot(xs, ys, color='lightgray', linestyle='--', linewidth=0.5)
        
    # longitude labels
    for lon in lon_labels:
        x, y = to_3413.transform(lon, lat_min)
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
        points = [to_3413.transform(lon, lat) for lon in lons]
        xs, ys = zip(*points)
        ax.plot(xs, ys, color='lightgray', linestyle='--', linewidth=0.5)    
    
    # Label latitudes at right
    for lat in lat_labels:
        x, y = to_3413.transform(lon_labels[-1], lat)
        ax.text(
            x - 5000,
            y - 10000,
            f"{lat:.1f}°N",
            ha='left',
            va='center',
            fontsize=8
        )


def add_scale(ax, cartopy_crs):
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
    
    
def add_true_north(ax, xmin, xmax, ymin, ymax):
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
    lon_ref, lat_ref = transformer['3413_4326'].transform(x_ref, y_ref)
    
    # move a small distance north
    lat_north = lat_ref + 0.5
    lon_north = lon_ref
    
    # convert degrees back to meters
    x_north, y_north = transformer['4326_3413'].transform(lon_north, lat_north)
    
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
    

#===================
#  Outlier detection
#===================

def detect_outliers(config, outlier_type='sd'):
    import matplotlib.pyplot as plt
    import matplotlib.colors as mcolors
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    import numpy as np
    import xarray as xr

    import pandas as pd
    from glob import glob
    from tqdm import tqdm
    import itertools
    
    # if outlier_type not in ['sd', 'md']:
    #     print(f"Undefined outlier type: {outlier_type}")
    #     exit()
    # elif outlier_type == 'sd':
    #     html_page='standard_deviation.html'
    #     outlier_desc='Standard Deviation'
    # elif outlier_type == 'md':
    #     html_page='mahalanobis_distance.html'
    #     outlier_desc='Mahalanobis Distance'
        
        
        
        
    print('    Detect outlier per scene...')
    outlier_dates = []
    quiver_payloads = []
    starts, ends = [], []
    
    # set list of files to process
    if config['batch_process']:
        sar_drift_dir = config['sar_drift_directory']
        gfilter_mask = "*_0050000m_*.txt*"
        gfilter_pattern = os.path.join(sar_drift_dir, gfilter_mask)
        gfilter_matches = sorted(glob(gfilter_pattern))
    else:
        gfilter_matches = [config['sar_drift_file_name']]
        
    
    

    for gfilter_path in tqdm(
            gfilter_matches,
            '    Creating outlier geopackages'
        ):
        
        # use 0075000m file instead of 0050000m
        # (always force txt extension)
        gfilter_path_75km = gfilter_path.replace(
            '_0050000m_',
            '_0075000m_',
        )
        
        gfilter_path_75km = f'{os.path.splitext(gfilter_path_75km)[0]}.txt'
        if os.path.exists(gfilter_path_75km):
            gfilter_path = gfilter_path_75km
    
    
        t1, t2 = _parse_pair_times(gfilter_path)
        starts.append(min(t1, t2))
        ends.append(max(t1, t2))
        

        df = read_sar_drift_data_file(
            input_file=gfilter_path,
            config=config
        )
        
        if df.shape[0] < config['ignore_vector_threshold']:
            # ignore files with few observations
            # print(f"skipping {os.path.basename(gfilter_path)} with {df.shape[0]} observations")
            continue
        
        
        
        # skip 75km file if MaxCorr2 > MaxCorr1 for < 60% of the data
        # if '_0075000m_' in gfilter_path:
        # if gfilter_path == gfilter_path: # always run
        #     pct_correct = (df['Maxcorr2'] > df['Maxcorr1']).mean() * 100
        #     if pct_correct < 60:
        #         # print(
        #         #     f"Reject file: {os.path.basename(gfilter_path)}\n"
        #         #     f"pct_correct={pct_correct:.1f}% (<60%)"
        #         # )
        #         continue
                

        # define outliers
        outlier_df, quiver_payloads_by_iter = outlier_search(
            df=df,
            config=config,
            radius_km=25,
            min_neighbors=8,
            outlier_type=outlier_type,
            iter_count = 2
        )
        
        # save intermediary outlier file
        basename=os.path.basename(gfilter_path)
        
        # create geopackage file
        verbose = config['verbose']
        config['verbose'] = False
        gdf_points, gdf_lines = create_shape_package(
                df=outlier_df,
                base_name=basename,
                config=config
        )
        config['verbose'] = verbose
        
        
        
        # draw inlier quivers on supplied PNG file
        # Plot SAR drift vectors

    
        crs_3413 = ccrs.NorthPolarStereo(central_longitude=-45)
        # Note: Cartopy's NorthPolarStereo aligns with EPSG:3413 for most use cases,
        # but EPSG:3413 has specific parameters. If you need exact EPSG:3413,
        # we can define it via PROJ string; usually this is fine for coastlines.
    
        fig = plt.figure(figsize=(10, 10))
        ax = plt.axes(projection=crs_3413)
    
        # Set extent in the projection's coordinate system (meters)
        pad = 100_000 # 10km
        xmin = np.round(outlier_df["X1"].min() - pad, 3)
        xmax = np.round(outlier_df["X1"].max() + pad, 3)
        ymin = np.round(outlier_df["Y1"].min() - pad, 3)
        ymax = np.round(outlier_df["Y1"].max() + pad, 3)

        ax.set_extent([xmin, xmax, ymin, ymax], crs=crs_3413)
    
        # Coastlines / land
        ax.add_feature(cfeature.LAND, zorder=0)
        ax.coastlines(resolution="10m", linewidth=1.0, zorder=1)
    
        mask_inlier = outlier_df["outlier_category"].isin(["00", "01"])
        
        inlier_X = outlier_df.loc[mask_inlier, "X1"].to_numpy()
        inlier_Y = outlier_df.loc[mask_inlier, "Y1"].to_numpy()
        inlier_u = outlier_df.loc[mask_inlier, "dx"].to_numpy()
        inlier_v = outlier_df.loc[mask_inlier, "dy"].to_numpy()

        outlier_X = outlier_df.loc[~mask_inlier, "X1"].to_numpy()
        outlier_Y = outlier_df.loc[~mask_inlier, "Y1"].to_numpy()
        outlier_u = outlier_df.loc[~mask_inlier, "dx"].to_numpy()
        outlier_v = outlier_df.loc[~mask_inlier, "dy"].to_numpy()
        
        quiver_payloads.append({
            "X": outlier_df["X1"].to_numpy(),
            "Y": outlier_df["Y1"].to_numpy(),
            "u": outlier_df["dx"].to_numpy(),
            "v": outlier_df["dy"].to_numpy()
        })
        
        ax.quiver(
            inlier_X, inlier_Y, inlier_u, inlier_v,
            transform=crs_3413,
            angles="xy", scale_units="xy",
            scale=config['quiver_scale_small_area'],
            width=0.002, pivot="tail",
            color="green", zorder=2, label="inliers"
        )

        ax.quiver(
            outlier_X, outlier_Y, outlier_u, outlier_v,
            transform=crs_3413,
            angles="xy", scale_units="xy",
            scale=config['quiver_scale_small_area'],
            width=0.002, pivot="tail",
            color="red", zorder=2, label="outliers"
        )
        
        
        ax.set_title(
            f"Scene: {os.path.basename(gfilter_path)}\n"
            f"X {xmin} to {xmax}; Y {ymin} to {ymax}\n"
            f"Total observations: {outlier_df.shape[0]}"
        )
        
        ax.legend(loc="lower right")
        
        out_png_path = os.path.join(
            config['output_dir'],
            f'{basename}_inliers.png'
        )
        plt.savefig(out_png_path, dpi=150, bbox_inches="tight")
        plt.close(fig)


    # full plot
    
    # get sea ice extent from GMASI
    nc_path = r"D:\NOAA\Analysis\GMASI\GMASI-Snowice-2km_v1r0_blend_s202510150000000_e202510152359599_c202510160223347.nc"
    ds = xr.open_dataset(nc_path)
    ds = ds.sortby("Latitude")
    arctic_ds = ds["SnowIceMap"].sel(Latitude=slice(60, 90))
    # stride = 1
    # ice_ds = ice.isel(
    #     Latitude=slice(None, None, stride),
    #     Longitude=slice(None, None, stride),
    # )
    ice_mask = xr.where(arctic_ds == 3, 1.0, np.nan)
    lats = ice_mask["Latitude"].to_numpy()
    lons = ice_mask["Longitude"].to_numpy()
    lons_2d, lats_2d = np.meshgrid(lons, lats)
    
    
    # transformer = _set_transformer()
    # lons_X, lats_Y = transformer['4326_3413'].transform(lons_2d, lats_2d)
    
    
    crs_3413 = ccrs.NorthPolarStereo(central_longitude=-45)
    
    # compute global extent from all X/Y points
    # all_x = np.concatenate([p["X"] for p in quiver_payloads if len(p["X"])])
    # all_y = np.concatenate([p["Y"] for p in quiver_payloads if len(p["Y"])])
    
    # pad_m = 50_000  # 50 km padding
    # xmin, xmax = all_x.min() - pad_m, all_x.max() + pad_m
    # ymin, ymax = all_y.min() - pad_m, all_y.max() + pad_m
    all_mag = np.concatenate([
        np.hypot(p["u"], p["v"])/1000 for p in quiver_payloads if len(p["u"])
    ])

    
    norm = mcolors.Normalize(
        vmin=np.nanmin(all_mag),
        vmax=np.nanmax(all_mag)
    )
    
    fig = plt.figure(figsize=(12, 12))
    ax = fig.add_subplot(1, 1, 1, projection=crs_3413)
    # ax.set_extent([xmin, xmax, ymin, ymax], crs=crs_3413)
    ax.set_extent([-180, 180, 60, 90], crs=ccrs.PlateCarree())
    
    ax.add_feature(cfeature.LAND, facecolor="#efe8d8", zorder=0)
    ax.coastlines(resolution="10m", linewidth=1.0, zorder=2)
    # ax.set_facecolor("#cfe8f3") # ocean blue
    ax.set_facecolor("#bfe3f3")
    # sea ice
    ice_cmap = mcolors.ListedColormap(["#f7f7f7"]) # sea ice as off-white
    ax.pcolormesh(
        lons_2d, lats_2d, ice_mask.to_numpy(),
        transform=ccrs.PlateCarree(),
        cmap=ice_cmap,
        shading="nearest",
        alpha=1.0,
        zorder=1, # display in layer below the coastlines
        edgecolors="none",
        linewidth=0,
        antialiased=False,
        rasterized=True
    )
    
    q_for_cbar = None  # keep one Quiver artist to attach the colorbar
    
    
    for p in quiver_payloads:
        if len(p["X"]) == 0:
            continue
        
        step = config['inlier_vector_stride']
        X = p["X"][::step]; Y = p["Y"][::step]
        u = p["u"][::step]; v = p["v"][::step]
        M = np.hypot(u, v)/1000 # km
    
        q = ax.quiver(
            X, Y, u, v, M,   # <-- M colors the arrows
            transform=crs_3413,
            angles="xy",
            scale_units="xy",
            scale=config['quiver_scale_large_area'],
            width=0.001,
            pivot="tail",
            cmap="viridis",
            norm=norm,
            zorder=2
        )
    
        if q_for_cbar is None:
            q_for_cbar = q
    
    # add magnitude legend (colorbar)
    if q_for_cbar is not None:
        cbar = fig.colorbar(q_for_cbar, ax=ax, orientation="vertical", shrink=0.65, pad=0.02)
        cbar.set_label("Vector velocity (km_day)")
        
        ax.quiverkey(q_for_cbar, 1.05, 0.08, 10_000, "10 km", labelpos="E", coordinates="axes")
        ax.quiverkey(q_for_cbar, 1.05, 0.06, 20_000, "20 km", labelpos="E", coordinates="axes")
        ax.quiverkey(q_for_cbar, 1.05, 0.04, 30_000, "30 km", labelpos="E", coordinates="axes")            
    
    ax.set_title(
        "All inlier vectors colored by magnitude\n"
        f"from {min(starts)} to {max(ends)}"
    )
    import matplotlib.patches as mpatches
    leg = ax.legend(
        handles=[
            mpatches.Patch(
                facecolor="#f7f7f7",
                edgecolor="#555555",
                linewidth=0.5,
                label="Sea ice"
            )
        ],
        loc="lower left",
        frameon=True,
        framealpha=1.0,
        fancybox=True
    )
    leg.get_frame().set_edgecolor("#555555")
    leg.get_frame().set_linewidth(1.0)
    
    out_png_path = os.path.join(config["output_dir"], "all_inliers.png")
    plt.savefig(out_png_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    
    
    
    # # create slide image for each iteration
    # import plotly.graph_objects as go
    
    # def segments(X, Y, u, v):
    #     # build x,y arrays with None gaps between segments
    #     xs = np.column_stack([X, X + u, np.full_like(X, np.nan)]).ravel()
    #     ys = np.column_stack([Y, Y + v, np.full_like(Y, np.nan)]).ravel()
    #     xs = np.where(np.isnan(xs), None, xs)
    #     ys = np.where(np.isnan(ys), None, ys)
    #     return xs, ys
    
    
    # line_style = dict(width=2)
    
    
    # frames = []
    # for k, p in enumerate(quiver_payloads_by_iter):
    #     xs, ys = segments(p["X"], p["Y"], p["u"], p["v"])
    #     frames.append(
    #         go.Frame(
    #             name=str(k+1),
    #             data=[go.Scattergl(
    #                 x=xs, y=ys, mode="lines", line=line_style
    #             )],
    #             traces=[0]
    #         )
    #     )
    
    # # initial
    # xs0, ys0 = segments(**quiver_payloads_by_iter[0])
    
    # fig = go.Figure(
    #     data=[go.Scattergl(x=xs0, y=ys0, mode="lines", line=line_style)],
    #     frames=frames
    # )
    
    # fig.update_layout(
    #     title="Vectors by iteration",
    #     xaxis=dict(scaleanchor="y"),  # keep aspect ratio
    #     sliders=[{
    #         "steps": [
    #             {
    #                 "method": "animate",
    #                 "label": str(k+1),
    #                 "args": [
    #                     [str(k+1)],
    #                     {
    #                         "mode": "immediate",
    #                         "frame": {"duration": 0, "redraw": True},
    #                         "transition": {"duration": 0},
    #                     }
    #                 ],
    #             }
    #             for k in range(len(frames))
    #         ]
    #     }],
    #     updatemenus=[{
    #         "type": "buttons",
    #         "showactive": False,
    #         "buttons": [
    #             {
    #                 "label": "Play",
    #                 "method": "animate",
    #                 "args": [
    #                     None,
    #                     {
    #                         "fromcurrent": True,
    #                         "mode": "immediate",
    #                         "frame": {"duration": 300, "redraw": True},
    #                         "transition": {"duration": 0},
    #                     }
    #                 ]
    #             },
    #             {
    #                 "label": "Pause",
    #                 "method": "animate",
    #                 "args": [
    #                     [None],
    #                     {
    #                         "mode": "immediate",
    #                         "frame": {"duration": 0, "redraw": False},
    #                         "transition": {"duration": 0},
    #                     }
    #                 ]
    #             }
    #         ]
    #     }]
    # )
    # fig.show()
    # # exit()
    
    # # optional: save interactive HTML
    # fig.write_html(r"D:\NOAA\GitHub\buoy_eda\output\iterations\vectors_by_iteration.html")
    
    
def outlier_search(df, config, outlier_type,
                   radius_km=20, min_neighbors=10, iter_count=1):
    import numpy as np
    from scipy.spatial import cKDTree
    # from sklearn.covariance import MinCovDet
    # from scipy.stats import chi2
    
    out_df = df.reset_index(drop=True).copy()
    
    mahal_sq_scores = []
    mahal_outlier_flags = []
    radius_m = radius_km * 1000
    iter_prev_inliers = None
    quiver_payloads_by_iter = []
    
    # create scene groupings based on `File` and `File2` values
    out_df = out_df.sort_values(by=['File1', 'File2'], ascending=True)
    out_df = out_df.reset_index(drop=True) # reset index after sorting
    out_df["bearing_rad"] = np.deg2rad(out_df["Bear_deg"].to_numpy())
    out_df["b_sin"] = np.sin(out_df["bearing_rad"])
    out_df["b_cos"] = np.cos(out_df["bearing_rad"])
    out_df["outlier_category"] = '01' # default value of significant inlier
    out_df["neighbor_indices"] = None
    out_df["neighbor_count"] = 0
    out_df["distance_z_score"] = np.nan
    out_df["bearing_z_score"] = np.nan
    
    out_df["scene"] = out_df.groupby(
        ['File1', 'File2'],
        sort=False
    ).ngroup() + 1
    out_df.to_csv(os.path.join(config['output_dir'], 'grouped.csv'))
    
    


    
    for iter_idx in range(iter_count):
        # iteratively run outlier detection until no new outliers found
        # instantiate pool data frame
        pool_df = out_df[out_df['outlier_category'].isin(['00', '01'])].copy() # keep any inliet whether confident or not
        inlier_count = (out_df['outlier_category'] == '01').sum()
        
        
        quiver_payloads_by_iter.append({
            "X": pool_df["X1"].to_numpy(),
            "Y": pool_df["Y1"].to_numpy(),
            "u": pool_df["dx"].to_numpy(),
            "v": pool_df["dy"].to_numpy()
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
            # Xall = scene_df[['U_kmdy', 'V_kmdy', 'b_sin', 'b_cos']].to_numpy() # just bearing rads (not sin & cos)
            # scene_df.to_csv(fr'D:\NOAA\GitHub\buoy_eda\output\scenes\{scene_df["File1"].iloc[0]}___{scene_df["File2"].iloc[0]}.csv')
            
            for local_idx, local_neighbors in enumerate(all_neighbors):
                
                # drop self
                neigh_idxs = [
                    j for j in local_neighbors if j != local_idx
                ]
                
                target_out_idx = scene_df.index[local_idx]
                
                if len(neigh_idxs) == 0:
                    out_df.at[target_out_idx, "neighbor_indices"] = None
                    out_df.at[target_out_idx, "neighbor_count"] = 0
                    out_df.at[target_out_idx, "distance_z_score"] = np.nan
                    out_df.at[target_out_idx, "bearing_z_score"] = np.nan
                    continue
                
                neigh_rows = scene_df.iloc[neigh_idxs]

                neigh_dist = neigh_rows['total_distance_km'].to_numpy()
                neigh_bear = neigh_rows['bearing_rad'].to_numpy()
                
                # compute neighbor mean and standard deviation
                dist_mean = np.nanmean(neigh_dist)
                dist_std = np.nanstd(neigh_dist)
                bear_mean = circular_mean(neigh_bear)
                bear_std = circular_std(neigh_bear)
                
                # get current cell values
                cell_dist = scene_df.iloc[local_idx]["total_distance_km"]
                cell_bear = scene_df.iloc[local_idx]["bearing_rad"]
                
                # compute z-score
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
    
                
                out_df.at[target_out_idx, "neighbor_indices"] = neigh_out_idx
                out_df.at[target_out_idx, "neighbor_count"] = len(neigh_out_idx)
                out_df.at[target_out_idx, "distance_z_score"] = np.round(dist_z_score, 3)
                out_df.at[target_out_idx, "bearing_z_score"] = np.round(bear_z_score, 3)
                
                
                # # Mahalanobis distance
                # if outlier_type=='md':
                #     x = Xall[idx, :] # target vector
                #     Xn = Xall[neigh_idxs, :] # neighbor matrix
                    
                #     # standardize data
                #     mu = Xn.mean(axis=0)
                #     sd = Xn.std(axis=0)
                #     sd[sd == 0] = 1.0
                #     Xn_z = (Xn - mu) / sd
                #     x_z = (x - mu) / sd
    
                    
                #     # # Need enough neighbors to estimate covariance robustly
                #     p = Xn.shape[1]
                #     if len(neigh_idxs) < 5:
                #         mahal_sq = np.nan
                #     else:
                #         mcd = MinCovDet().fit(Xn_z)
                #         mahal_sq = mcd.mahalanobis([x_z])[0]  # squared distance
                    
                #     alpha = 0.5
                #     thr_sq = chi2.ppf(alpha, df=p)  # squared-distance threshold
                #     is_outlier = (mahal_sq > thr_sq)
                    
                #     mahal_sq_scores.append(mahal_sq)
                #     mahal_outlier_flags.append(int(is_outlier))
                # else:
                #     mahal_sq_scores.append(np.nan)
                #     mahal_outlier_flags.append(0)
                

                
 
                
                
        """
        assign outlier category
        00: None (under neighbor threshold)
        01: None (equal to or above neighbor threshold)
        10: Distance (under neighbor threshold)
        11: Distance (equal to or above neighbor threshold)
        20: Bearing (under neighbor threshold)
        21: Bearing (equal to or above neighbor threshold)
        30: Distance and bearing (under neighbor threshold)
        31: Distance and bearing (equal to or above neighbor threshold)
        """
        distance_filter = out_df['distance_z_score'] > 3
        bearing_filter = out_df['bearing_z_score'] > 3
        base_cat = np.select(
            [
                distance_filter & ~bearing_filter,
                ~distance_filter & bearing_filter,
                distance_filter & bearing_filter, 
            ],
            [1, 2, 3],
            default=0
        ).astype(np.int8)
        statistical_confidence_flag = (
            out_df["neighbor_count"] >= min_neighbors
        ).astype(np.int8) # force 0/1 not True/False
        out_df["outlier_category"] = (
            base_cat.astype(str) + statistical_confidence_flag.astype(str)
        )
                    

        # review_columns = ['outlier_category', 'neighbor_indices', 'neighbor_count', 'distance_z_score', 'bearing_z_score']
        # out_df[review_columns].to_csv(fr'D:\NOAA\GitHub\buoy_eda\output\iterations\{iter_idx+1}.csv')                    
    
   
    return out_df, quiver_payloads_by_iter    


    
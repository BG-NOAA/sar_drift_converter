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


def _polar_lonlat_to_xy(longitude, latitude, true_scale_lat,
                        re, e, hemisphere):
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

def _download_sar_drift_files(config):
    """
    Download Arctic-wide SAR ice drift gfilter text files from a
    configured web directory.

    Scrapes the HTML directory listing at the URL specified in
    `config['sar_drift_data_url']`, filters for matching gfilter
    filenames, and downloads any files not already present in the
    local SAR drift directory.

    Args:
        config (dict): Configuration dictionary. Must include:
                - 'sar_drift_data_url' (str): URL of the directory
                  listing page hosting SAR drift gfilter text files.
                - 'sar_drift_directory' (str): Local directory path
                  where downloaded files are saved.

    Workflow:
        1. Send a GET request to `config['sar_drift_data_url']` and
           parse the HTML directory listing using BeautifulSoup.
        2. Filter all `<a>` href links for filenames matching the
           gfilter pattern: `SARIceDrift_EG125_*.txt`.
        3. Skip links beginning with `?` or `/` (navigation and
           parent directory entries).
        4. For each matched file, skip download if the file already
           exists in `config['sar_drift_directory']`.
        5. Download new files via streaming GET requests in 1 MB
           chunks, logging each download URL.
        6. Log and return early if no matching files are found.

    Returns:
        None

    Raises:
        requests.HTTPError: If the directory listing request or any
            individual file download returns a non-2xx status code,
            via `raise_for_status()`.
        requests.RequestException: If a network error occurs during
            any GET request.

    Notes:
        - SSL verification is disabled for all requests via
          `verify=False`. InsecureRequestWarning is suppressed via
          `urllib3.disable_warnings()`.
        - Files already present in `config['sar_drift_directory']`
          are skipped silently, making repeated calls safe for
          incremental updates.
        - `base_url` is normalized to end with `/` before constructing
          absolute download links via `urljoin`, preventing the final
          path component from being dropped.
        - Download progress is displayed via a `tqdm` progress bar.
    """
    
    import logging
    from tqdm import tqdm
    import os
    import requests
    from bs4 import BeautifulSoup
    from urllib.parse import urljoin
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    # log activity
    logger = logging.getLogger('sar_drift_converter')

    
    # download SAR drift data files
    base_url = config['sar_drift_data_url'].rstrip('/') + '/'
    
    # Get the HTML page content
    response = requests.get(base_url, verify=False)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract all <a> tag hrefs
    links = []
    for a in soup.find_all('a', href=True):
        if not a['href'].startswith('?') and not a['href'].startswith('/'):
            links.append(a['href'])
    
    
    # Filter for Arctic-wide gfilter.txt files
    download_links = []
    for link in links:
        if link.startswith('SARIceDrift_EG125_') and \
           link.endswith('T2359_gfilter1.txt') and \
           'T0000_' in link:
               download_links.append(urljoin(base_url, link))
    
    
    # Download each file                
    if len(download_links) == 0:
        logger.info("No new gfilter files found to download")
        return
    
    download_folder = config['sar_drift_directory']        
    tqdm_desc = "Downloading SAR drift gfilter files"
    for file_url in tqdm(download_links, desc=tqdm_desc, unit='file'):
        filename = os.path.basename(file_url)
        local_path = os.path.join(download_folder, filename)
        
        # Overwrite if already downloaded
        try:
            with requests.get(file_url, stream=True, verify=False) as r:
                r.raise_for_status()
                with open(local_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=1048576):
                        f.write(chunk)
            logger.info(f"Downloaded {filename}")
        except requests.exceptions.HTTPError as e:
            logger.warning(f"Skipping {filename}: {e}")


def _read_gfilter_file(args):
    """
    Resolve the correct file path for a single gfilter entry and read it
    into a raw DataFrame. Intended for use as a module-level worker
    function with ProcessPoolExecutor.
 
    Checks whether a 75 km counterpart exists for the given 50 km file and
    reads the 75 km version if so. Adds `_use_75km` and `_source_file`
    columns to the returned DataFrame. The returned DataFrame contains only
    EPSG-independent columns as produced by `util.read_sar_drift_data_file`;
    projection-dependent columns are added later by `util._apply_projection`.
 
    This function must be defined at module level (not nested inside another
    function) so that it can be pickled by ProcessPoolExecutor on Windows,
    where the `spawn` start method is used.
 
    Args:
        args (tuple): A two-element tuple of (gfilter_path, config) where
            gfilter_path (str) is the path to the 50 km gfilter file and
            config (dict) is the configuration dictionary passed directly
            to `util.read_sar_drift_data_file`. Must include `delimiter`.
 
    Returns:
        pandas.DataFrame: Single-file raw DataFrame with `_use_75km` (bool)
            and `_source_file` (str) columns appended.
 
    Raises:
        Exception: Re-raises any exception encountered during file reading,
            causing the ProcessPoolExecutor in the caller to terminate and
            propagate the error to the main process. Processing halts
            immediately on failure.
 
    Notes:
        - File extensions containing an underscore suffix (e.g. '.txt_0')
          are normalized by truncating at the first underscore before the
          75 km path substitution is attempted.
        - The 75 km counterpart path is derived by replacing `_0050000m_`
          with `_0075000m_` in the normalized path. If the path is unchanged
          or the 75 km file does not exist, the original path is used.
        - Header row detection is handled automatically inside
          `util.read_sar_drift_data_file` via `_detect_skip_rows`.
    """
    
    import util
    import os

    gfilter_path, config = args

    basename, ext = os.path.splitext(gfilter_path)
    if '_' in ext:
        ext = ext.split('_')[0]
    normalized = basename + ext

    path_75km = normalized.replace('_0050000m_', '_0075000m_')
    use_75km = (path_75km != normalized and os.path.exists(path_75km))
    read_path = path_75km if use_75km else gfilter_path

    try:
        df = util.read_sar_drift_data_file(input_file=read_path, config=config)
        df['_use_75km'] = use_75km
        df['_source_file'] = os.path.basename(read_path)
        return df
    except Exception as e:
        import traceback
        print(
            f"ERROR reading {os.path.basename(read_path)}: "
            f"{type(e).__name__}: {e}"
        )
        traceback.print_exc()
        raise
    

def _check_existing_files(scene_output_stub, config):
    """
    Check which expected daily output files already exist for a given day.

    Returns a dictionary mapping each output type to a bool indicating
    whether that file already exists on disk. This allows the processing
    loop to skip only the specific outputs that are already present rather
    than skipping the entire day, enabling partial-day resume after an
    interrupted run.

    Args:
        scene_output_stub (dict): Lightweight dict containing date bounds
            for the day being checked. Must contain:
                - `start_date` (pandas.Timestamp): Minimum date_start for
                  the day.
                - `end_date`   (pandas.Timestamp): Maximum date_end for
                  the day.
        config (dict): Configuration dictionary. Must include:
                - `file_server` (str): Root output path.
                - `epsg` (int): Target projected CRS code.
                - `level` (str): Processing level ('00'–'03').
                - `version` (str): Version string for filename construction.
                - `overwrite` (bool): If True, all values are returned as
                  False regardless of file existence, except `json` which
                  is returned as True for levels that do not produce JSON
                  output ('01', '02').

    Returns:
        dict: Keys are output type strings, values are bool indicating
            whether the file exists on disk. Possible keys:
                - `nc_scenes` (bool): Multi-layer scenes NetCDF.
                - `nc_daily`  (bool): Single-layer daily NetCDF.
                - `gpkg`      (bool): GeoPackage. Always True for levels
                  that do not produce GeoPackage output ('01').
                - `json`      (bool): Vector JSON data file. Always True
                  for levels that do not produce JSON output ('01', '02').
            If `config['overwrite']` is True, all values are False except
            `json`, which is True for levels '01' and '02'.

    Notes:
        - The checked paths mirror exactly the paths written by
          `create_daily_output` for the same level/EPSG/version combination.
        - `gpkg` and `json` are set to True (treated as already existing)
          for levels that never produce those outputs, so callers can check
          `all(exists.values())` uniformly to decide whether to skip a day
          entirely.
        - GeoPackage is produced for levels '00', '02', and '03'. The
          existence check uses the daily base filename with a `.gpkg`
          extension under `<file_server>/<epsg>/<level>/<year>/gpkg/`.
        - JSON is produced for levels '00' and '03' only. The existence
          check looks for `si_velocity_<start>.json` under
          `<file_server>/<epsg>/<level>/data/`.
        - When `overwrite` is True, all values are False for levels that
          produce that output type, causing those outputs to be regenerated
          unconditionally.
    """
    
    import os
    import pandas as pd
    import logging 
    
    overwrite = config['overwrite']
    start_date = scene_output_stub['start_date']
    reprocess_days = config['reprocess_days']
    cutoff = (
        pd.Timestamp.now().normalize() - pd.Timedelta(days=reprocess_days)
    )
    if start_date >= cutoff:
        # always rewrite output for the number of days in `reprocess_days`
        # this allows for corrections/updates from website
        overwrite = True
        logger = logging.getLogger('sar_drift_converter')
        logger.info(
            f'Recreating output since {start_date} is within repcoess window '
            f'of {reprocess_days} days from run time'
        )
    
    
    # overwirte indicates always create the file even if existing
    if overwrite:
        if config['level'] == '00':
            return {
                'nc_scenes': False,
                'nc_daily':  False,
                'gpkg':      False,
                'json':      False
            }
        elif config['level'] == '01':
            return {
                'nc_scenes': False,
                'nc_daily':  False,
                'gpkg':      True,
                'json':      True
            }
        elif config['level'] == '02':
            return {
                'nc_scenes': False,
                'nc_daily':  False,
                'gpkg':      False,
                'json':      True
            }
        elif config['level'] == '03':
            return {
                'nc_scenes': True,
                'nc_daily':  False,
                'gpkg':      False,
                'json':      False
            }


    start = scene_output_stub['start_date'].strftime('%Y%m%d')
    end   = scene_output_stub['end_date'].strftime('%Y%m%d')
    epsg  = str(config['epsg'])
    lvl   = f"Processing Level - {config['level']} (PL{config['level']})"
    yr    = start[:4]
    nc_dir   = os.path.join(config['file_server'], epsg, lvl, yr, 'nc')
    gpkg_dir = os.path.join(config['file_server'], epsg, lvl, yr, 'gpkg')
    data_dir = os.path.join(config['file_server'], epsg, lvl, 'data')


    # check NetCDF scenes
    nc_scenes_exists = True
    if config['level'] in ['00', '01', '02']:
        nc_scenes_exists = os.path.exists(os.path.join(
            nc_dir,
            f"SIVelocity_SAR_{start}_{end}_scenes_12km_NH_{config['epsg']}"
            f"_PL{config['level']}_v{config['version']}.nc"
        ))
        
    # check NetCDF daily
    nc_daily_exists = True
    if config['level'] in ['00', '01', '02', '03']:
        nc_daily_exists = os.path.exists(os.path.join(
            nc_dir,
            f"SIVelocity_SAR_{start}_{end}_daily_12km_NH_{config['epsg']}"
            f"_PL{config['level']}_v{config['version']}.nc"
        ))

    # check GeoPackage
    gpkg_exists = True
    if config['level'] in ['00', '02', '03']:
        gpkg_exists = os.path.exists(os.path.join(
            gpkg_dir,
            f"SIVelocity_SAR_{start}_{end}_daily_12km_NH_{config['epsg']}"
            f"_PL{config['level']}_v{config['version']}.gpkg"
        ))
        
    # check JSON (check both since buoy data are a day behind SAR drift data)
    si_json_exists = True
    if config['level'] in ['00', '03']:
        si_json_exists = os.path.exists(
            os.path.join(data_dir, f"si_velocity_{start}.json")
        )
    buoy_json_exists = True
    if config['level'] in ['00', '03']:
        buoy_json_exists = os.path.exists(
            os.path.join(data_dir, f"buoy_velocity_{start}.json")
        )

    json_exists = si_json_exists and buoy_json_exists
    
   
    result = {
        'nc_scenes': nc_scenes_exists,
        'nc_daily': nc_daily_exists,
        'gpkg': gpkg_exists,
        'json': json_exists
    }
    return result


def _detect_skip_rows(input_file):
    """
    Peek at the input file to determine how many rows to skip before
    the header.

    Reads up to the first 10 lines and checks each one to see if it contains
    the expected header fields ('File1' and 'File2'). Returns the 0-based
    index of the header line, which is the number of rows pd.read_csv
    should skip.

    Args:
        input_file (str): Path to the SAR drift gfilter text file.

    Returns:
        int: Number of rows to skip (0 if header is on the first line).

    Raises:
        SystemExit: Via `util.error_msg` if no header row is found within
                    the first 10 lines.
    """
    
    with open(input_file, 'r') as f:
        for i, line in enumerate(f):
            if i >= 10:
                break
            if 'File1' in line and 'File2' in line:
                return i
            
            
    error_msg(
        "Could not locate header row ('File1', 'File2') in first 10 lines of "
        f"{input_file}"
    )
    
    
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
            - 'level' (str): Processing level used in the output .nc filename
                             (e.g. '03'). One of '00', '01', '02', '03'.

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
    
    
    cdl_file = os.path.join(config['meta_dir'], config['netcdf_cdl_file'])
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
        
    with xr.open_dataset(ncgen_ofile_nc, decode_times=False) as ds:
        # .load() pulls data into memory so the file can close
        return ds.load()


def _apply_projection(df_raw, epsg, config):
    """
    Apply a projected coordinate transformation to a raw SAR drift DataFrame.

    Reprojects start and end positions from EPSG:4326 to the target CRS
    specified by `epsg` using `_calculate_drift_daily`, then assigns all
    projection-dependent columns to a copy of the input DataFrame. Columns
    that are independent of projection - timestamps, raw geographic
    coordinates, duration, sensor identifiers, and source file metadata -
    are preserved unchanged from `df_raw`.

    This function is intended to be called once per EPSG after
    `combine_into_dataframe` has loaded and concatenated all raw input
    files, allowing the expensive parallel file I/O step to run exactly
    once regardless of how many target projections are required.

    Args:
        df_raw (pandas.DataFrame): Raw combined DataFrame as returned by
            `combine_into_dataframe` after `read_sar_drift_data_file` has
            been called for each file. Must contain the following columns:
                - 'latitude_1', 'longitude_1' (float): Start position
                  (EPSG:4326, degrees).
                - 'latitude_2', 'longitude_2' (float): End position
                  (EPSG:4326, degrees).
                - 'duration' (float): Observation duration in seconds.
        epsg (int): EPSG code for the target projected CRS
                    (e.g. 3413 for NSIDC Sea Ice Polar Stereographic North,
                    6931 for EASE-Grid 2.0 North).
        config (dict): Configuration dictionary. Must include:
                - 'speed_precision' (int): Decimal places for rounding speed,
                  displacement, and distance columns.
                - 'bearing_precision' (int): Decimal places for rounding
                  the bearing column.

    Returns:
        pandas.DataFrame: Copy of `df_raw` with the following columns
            added based on the target `epsg`:

            Projected coordinates (EPSG:`epsg`, metres):
                - 'X1' (float): x-coordinate of start position.
                - 'Y1' (float): y-coordinate of start position.
                - 'X2' (float): x-coordinate of end position.
                - 'Y2' (float): y-coordinate of end position.

            Displacement and velocity (EPSG:`epsg`):
                - 'sea_ice_x_displacement' (float): X2 − X1 (m), rounded
                  to `config['speed_precision']` decimal places.
                - 'sea_ice_y_displacement' (float): Y2 − Y1 (m), rounded
                  to `config['speed_precision']` decimal places.
                - 'u' (float): sea_ice_x_displacement / duration
                  (m s⁻¹).
                - 'v' (float): sea_ice_y_displacement / duration
                  (m s⁻¹).

            Speed and direction (geodesic, WGS84 ellipsoid):
                - 'sea_ice_speed' (float): Geodesic speed (m s⁻¹), rounded
                  to `config['speed_precision']` decimal places.
                - 'sea_ice_speed_kmdy' (float): Geodesic speed (km day⁻¹),
                  rounded to `config['speed_precision']` decimal places.
                - 'direction_of_sea_ice_displacement' (float): Forward
                  azimuth (degrees), rounded to
                  `config['bearing_precision']` decimal places.
                - 'distance' (float): Geodesic distance (m), rounded to
                  `config['speed_precision']` decimal places.

    Notes:
        - The returned DataFrame is a copy; `df_raw` is not modified.
        - Speed and direction columns (`sea_ice_speed`, `sea_ice_speed_kmdy`,
          `direction_of_sea_ice_displacement`, `distance`) are derived from
          the WGS84 geodesic and are mathematically independent of the target
          EPSG. They are computed here because `_calculate_drift_daily`
          produces them alongside the projection-dependent quantities.
        - `X1`, `Y1`, `X2`, `Y2`, `sea_ice_x_displacement`,
          `sea_ice_y_displacement`, `u_ms`, and `v_ms` will differ between
          EPSG:3413 and EPSG:6931 because the Cartesian axes of each
          projection are oriented differently.
        - A pyproj warning about database path setup is suppressed inside
          `_calculate_drift_daily` because it is expected in this runtime
          environment.
    """

    import numpy as np

    df = df_raw.copy()

    drift = _calculate_drift_daily(
        lat1=df['latitude_1'].values,
        lon1=df['longitude_1'].values,
        lat2=df['latitude_2'].values,
        lon2=df['longitude_2'].values,
        duration=df['duration'].values,
        epsg=epsg
    )

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
    df['u'] = np.round(drift['u'], config['displacement_precision'])
    df['v'] = np.round(drift['v'], config['displacement_precision'])
    df['sea_ice_speed'] = np.round(
        drift['speed_ms'], config['speed_precision']
    )
    df['sea_ice_speed_kmdy'] = np.round(
        drift['speed_kmdy'], config['speed_precision']
    )
    df['direction_of_sea_ice_displacement'] = np.round(
        drift['bearing'], config['bearing_precision']
    )
    df['distance'] = np.round(
        drift['distance'], config['displacement_precision']
    )
    df['distance_geod'] = np.round(
        drift['distance_geod'], config['displacement_precision']
    )

    return df


def _calculate_drift_daily(lat1, lon1, lat2, lon2, duration, epsg):
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
        duration (array-like): Observation duration in seconds
                                  (Time2_JS − Time1_JS).
        epsg (int): EPSG code for the target projected CRS used for
                    coordinate transformation and displacement computation
                    (e.g. 3413 for NSIDC Sea Ice Polar Stereographic North,
                    6931 for EASE-Grid 2.0).
 
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
                - 'u' : dx / duration  (m s⁻¹)
                - 'v' : dy / duration  (m s⁻¹)
 
            Speed:
                - 'speed_ms'   : distance / duration (m s⁻¹)
                - 'speed_kmdy' : (distance / 1000) / (duration / 86400)
                                  (km day⁻¹)
 
    Notes:
        - Projection is performed with `pyproj.Transformer` using
          `always_xy=True`, so longitude is passed before latitude.
        - Geodesic distance and forward azimuth are computed with
          `pyproj.Geod(ellps='WGS84').inv(lon1, lat1, lon2, lat2)`.
        - `u` and `v` are Cartesian velocity components in the target
          projection space. For EPSG:3413 the x-axis points roughly eastward
          and the y-axis roughly northward, but note that the source file's
          `U_vel_ms` / `V_vel_ms` fields use the opposite convention (U drives
          Y, V drives X). The values returned here are computed directly from
          projected displacements and are self-consistent.
        - `speed_ms` and `speed_kmdy` are derived from geodesic distance, not
          from `sqrt(dx² + dy²)`. They are therefore not exactly equal to
          `sqrt(u² + v²)` due to projection distortion; the discrepancy
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
        'u': dx / duration,
        'v': dy / duration,
        'speed_ms': distance / duration,
        'speed_kmdy':  (distance / 1000) / (duration / SECONDS_PER_DAY)
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


def _add_json_templates(data_dir, config):
    """
    Copy reference map template files into the viewer's data directory if
    they are not already present.

    Ensures that the static GeoJSON files required by the HTML viewer
    (land, coastline, graticules, grid) are available in `data_dir` before
    the viewer is served. Files that already exist at the destination are
    left untouched.

    Args:
        data_dir (str): Destination directory where template files must be
                        present. Typically the `data/` subdirectory adjacent
                        to the HTML viewer file.
        config (dict): Configuration dictionary. Must include:
                - 'meta_dir' (str): Directory containing the source template
                  files. Expected files are 'land.json', 'coastline.json',
                  'graticules.json', and 'grid.json'.

    Returns:
        None

    Notes:
        - Only missing files are copied; existing files are not overwritten.
        - `data_dir` must already exist before this function is called.
    """
    
    import os
    import shutil

    for template_name in config['geojson_templates']:
        src_path = os.path.join(config['meta_dir'], template_name)
        dest_path = os.path.join(data_dir, template_name)
        if not os.path.exists(dest_path):
            shutil.copy(src_path, dest_path)
    

def _download_uw_iabp_buoy_data(config):
    """
    Download and compile UW IABP buoy observation data for the date range
    covered by the current SAR drift dataset.

    Fetches the active buoy list from the UW IABP tables URL, downloads
    individual buoy `.txt` files, combines them into a single DataFrame,
    filters to the SAR drift date range, and saves the compiled output as
    a dated CSV file. If a matching compiled file already exists and
    `overwrite` is False, the existing file is loaded and validated instead.

    Args:
        config (dict): Configuration dictionary. Must include:
                - 'uw_iabp_buoy_url' (str): Base URL for individual buoy
                  `.txt` file downloads.
                - 'uw_iabp_buoy_tables' (str): URL of the `.js` file
                  listing active buoy identifiers.
                - 'uw_iabp_buoy_filename' (str): Base filename for the
                  compiled output CSV; the date range is appended
                  automatically.
                - 'buoy_dir' (str): Directory for downloaded buoy `.txt`
                  files and the compiled CSV.
                - 'start_date' (date): Minimum date_start from the SAR
                  drift data; used as the lower bound for filtering.
                - 'end_date' (date): Maximum date_start from the SAR
                  drift data; used as the upper bound for filtering.
                - 'overwrite' (bool): If True, re-download and recompile
                  even if a matching compiled file already exists.

    Returns:
        pandas.DataFrame: Compiled buoy observation DataFrame filtered
            to the SAR drift date range, with columns including
            `'time (UTC)'`, lat/lon positions, and buoy metadata.

    Raises:
        SystemExit: Via `error_msg` if the stored file's date range does
            not cover `config['start_date']`, indicating the buoy data
            needs to be re-downloaded.

    Notes:
        - The compiled CSV is named using the start and end dates:
          `<uw_iabp_buoy_filename>_<start_date>_<end_date>.csv`.
        - Individual buoy `.txt` files are saved to `buoy_dir` and
          reused on subsequent runs unless the buoy is active (recent
          observations may be incomplete until the buoy stops
          transmitting).
        - Data is only available from 2010 onward.
        - Observations with invalid coordinates or physically impossible
          values are filtered out.
        - Progress is displayed via `tqdm` during the download phase.
        - SSL verification is disabled via `urllib3.disable_warnings`.
    """
    
    import requests
    import os
    import glob
    import pandas as pd
    from tqdm import tqdm
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    import logging
    
    
    logger = logging.getLogger('sar_drift_converter')
    
    # Use previous file found for date range
    complete_buoy_data_file_basename = (
        os.path.splitext(config['uw_iabp_buoy_filename'])[0]
    )
    
    start_date_str  = config['start_date'].strftime('%Y-%m-%d')
    end_date_str  = config['end_date'].strftime('%Y-%m-%d')
    
    
    os.makedirs(config['buoy_dir'], exist_ok=True)
    complete_buoy_data_file = os.path.join(
        config['buoy_dir'],
        f'{complete_buoy_data_file_basename}_{start_date_str}_'
        f'{end_date_str}.csv'
    )
    
    
    if os.path.exists(complete_buoy_data_file) and not config['overwrite']:
        logger.info(
            "Loading previously downloaded data file | "
            f"{complete_buoy_data_file}"
          )
        df = pd.read_csv(
            complete_buoy_data_file,
            delimiter=',',
            header=0,
            low_memory=False
        )
        
        # check start and end dates match  the corresponding dates
        # in stored data file before continuing
        df['time (UTC)'] = pd.to_datetime(df['time (UTC)'])
        min_date = df['time (UTC)'].dt.date.min()
        max_date = df['time (UTC)'].dt.date.max()
        if min_date < config['start_date']:
            error_msg(
                f"The start date in the stored file {min_date} does not "
                "match the SAR drift data start date"
                f"{config['start_date']}. The buoy data needs to be "
                "downloaded. Either set `overwrite`=true in config file or "
                f" delete {complete_buoy_data_file}"
            )

        if max_date > config['end_date']:
            error_msg(
                f"The end date in the stored file {max_date} does not "
                "match the SAR drift data end date"
                f"{config['end_date']}. The buoy data needs to be "
                "downloaded. Either set `overwrite`=true in config file or "
                f" delete {complete_buoy_data_file}"
            )
        
        return df
    
    
    # get high-level buoy attributes
    url = config['uw_iabp_buoy_tables']
    js_text = requests.get(url, verify=False).text
    data_entries = js_text.split('\n')
    
    cols = [
        'BuoyID', 'WMO', 'Start Year', 'Buoy Type', 'Owner', 'Logistics', 
        'Latest Report', 'Latest Latitude', 'Latest Longitude',
        'Latest BP', 'Latest Ts', 'Latest Ta'
    ]
    buoy_data = []
    for entry in data_entries:
        if entry.startswith('['):
            # convert entry into a list
            entry = entry.replace('"', '').replace('[', '').replace(']','')
            entry_list = entry.split(',')                                  
            buoy_data.append(entry_list[0:12]) # only take 12 columns
    df_buoy_table = pd.DataFrame(columns=cols, data=buoy_data)
    
    # fix `Latest Report` column set NaN to 2012-12-31 00:00:00
    df_buoy_table['Latest Report'] = pd.to_datetime(
        df_buoy_table['Latest Report'], errors='coerce'
    )
    default_date = pd.Timestamp("2012-12-31 00:00:00")
    df_buoy_table['Latest Report'] = (
        df_buoy_table['Latest Report'].fillna(default_date)
    )


    df_buoy_table['report_date'] = (
        df_buoy_table['Latest Report'].dt.strftime('%Y-%m-%d')
    )
        
    
    # Filter buoys whose latest report falls within the configured date range    
    date_range_mask = (
        (df_buoy_table['report_date'].notna()) &
        (df_buoy_table['report_date'] >= start_date_str) &
        (df_buoy_table['report_date'] <= end_date_str)
    )
    in_range_buoy_list = df_buoy_table.loc[date_range_mask, 'BuoyID'].unique()
    
    
    # download each buoy file
    logger.info(
        f"Downloading UW IABP buoy data | {config['start_date']} "
        f"to {config['end_date']} | Total buoys {len(in_range_buoy_list)}"
    )
    for buoy_id in tqdm(
            in_range_buoy_list,
            desc='Downloading buoy data',
            unit='buoy file'
        ):
        logger.info(f"Downloading buoy {buoy_id}")
        buoy_file = os.path.join(config['buoy_dir'], f"{buoy_id}.txt")
        url = f"{config['uw_iabp_buoy_url']}?bid={buoy_id}"
        buoy_text = requests.get(url, verify=False).text
        with open(buoy_file, 'w', encoding='utf-8') as txt:
            txt.write(buoy_text)

            
    # create new complete buoy data CSV file
    downloaded_buoy_list = []
    for buoy_path in tqdm(glob.glob(os.path.join(
            config['buoy_dir'], '*.txt')),
            desc='Building complete buoy data file',
            unit='buoy'
        ):
        if 'copy' in buoy_path:
            # corrupted downloaded files with have `copy` in file name
            continue
        
        with open(buoy_path, 'r', encoding='UTF-8') as txt:
            for idx, line in enumerate(txt):
                line = line.strip()
                if line and idx > 0: # skip heading
                    downloaded_buoy_list.append(line.split(','))


    # create data frame of all downloaded buoys
    df = pd.DataFrame(downloaded_buoy_list)
    df = df.iloc[:, [0, 1, 4, 6, 7]].copy()
    df.columns = ['BuoyID', 'Year', 'DOY', 'Lat', 'Lon']
    df['Year'] = df['Year'].astype(int)
    df['DOY']  = df['DOY'].astype(float)
    base_year = pd.to_datetime(df['Year'].astype(str), format='%Y')
    full_datetime = base_year + pd.to_timedelta(df['DOY'] - 1, unit='D')
    df['time (UTC)'] = full_datetime
    df['date'] = df['time (UTC)'].dt.strftime('%Y-%m-%d')
    df.drop(['Year', 'DOY'], axis=1, inplace=True)
    
    
    # reduce observations to match start and end dates
    date_filter = (
        (df['date'] >= start_date_str) &
        (df['date'] <= end_date_str)
    )
    df = df[date_filter]
    
    
    # rename geographic coordinate columns
    df.rename(columns={
        'BuoyID': 'buoy_id',
        'Lon': 'lon',
        'Lat': 'lat'
    }, inplace=True)
    df['lat'] = df['lat'].astype(float)
    df['lon'] = df['lon'].astype(float)

    df.to_csv(complete_buoy_data_file, index=False)
    
    return df


def _load_buoy_data(config):
    import numpy as np
    import pandas as pd
    import logging
    from tqdm import tqdm
    
    print('Opening buoy data file...')
    
    logger = logging.getLogger('sar_drift_converter')
    
    df = _download_uw_iabp_buoy_data(config)
    df['time (UTC)'] = pd.to_datetime(
        df['time (UTC)'], format='%Y-%m-%dT%H:%M:%SZ'
    )
    
    logger.info(f'Loaded buoy data | {df.shape[0]} rows')
        
    # Filter out buoys below 50°N (outside Arctic/sub-Arctic)
    # region of interest
    df_filter = (df['lat'] >= 50.0)
    df = df[df_filter].copy()
    
    
    # If -180 appears for lon and -90 appears for lat,
    # it is a false reading. Also filter out invalid coordiantes!           
    df_filter = (
        (df['lat'] != -90.0) &
        (df['lon'] != -180.0) &
        (df['lat'].between(-90.0, 90.0)) &
        (df['lon'].between(-180.0, 360.0))
    )            
    df = df[df_filter].copy()

   
    # Take the first observation of each day per buoy regardless of hour,
    # since hour==0 is unreliable. Some buoys report multiple times in the
    # first hour and some days have no midnight observation at all
    df = (
        df.groupby(['buoy_id', 'date'], as_index=False)
          .first()
          .sort_values(['buoy_id', 'time (UTC)'])
    )
    
    buoys_skipped = []
    drift_results = []
    
    buoy_groups = list(df.groupby('buoy_id'))
    for buoy_id, df_buoy in tqdm(
            buoy_groups, desc='Processing buoys', unit='buoy'
        ):
    
        # Cannot track buoys without zero-hour observations
        if df_buoy.shape[0] == 0:
            buoys_skipped.append(f'{buoy_id}: no zero-hour observations')
            continue

        
        # Skip buoy if there is just one observation
        # (no drift interval possible)
        first_obs = df_buoy['date'].iloc[0]
        last_obs  = df_buoy['date'].iloc[-1]
        if first_obs == last_obs:
            buoys_skipped.append(f'{buoy_id}: only one observation')
            continue
        
                
        """
        For each buoy, create two aligned slices of the midnight-only rows:
          starts = every row except the last
          ends   = every row except the first
        When paired by position, each start row lines up with the very next
        midnight observation for that buoy, forming one drift interval per row.
        `groupby` ensures the last row of one buoy never bleeds into the
        next buoy.
        """
        starts = df_buoy.iloc[:-1].reset_index(drop=True)
        ends   = df_buoy.iloc[1:].reset_index(drop=True)
    
        drift_df = pd.DataFrame({
            'buoy_id':     starts['buoy_id'],
            'date':        starts['date'],
            'latitude_1':  starts['lat'],
            'longitude_1': starts['lon'],
            'latitude_2':  ends['lat'],
            'longitude_2': ends['lon'],
            'duration':    (
                ends['time (UTC)'] - starts['time (UTC)']
            ).dt.total_seconds()
        })
    
        
        drift = pd.DataFrame(_calculate_drift_daily(
            lat1=drift_df['latitude_1'].values,
            lon1=drift_df['longitude_1'].values,
            lat2=drift_df['latitude_2'].values,
            lon2=drift_df['longitude_2'].values,
            duration=drift_df['duration'].values,
            epsg=config['epsg']
        ))
        drift.insert(0, 'buoy_id', drift_df['buoy_id'].values)
        drift.insert(1, 'date', drift_df['date'].values)
        drift.insert(2, 'latitude_1', drift_df['latitude_1'].values)
        drift.insert(3, 'longitude_1', drift_df['longitude_1'].values)
        drift.insert(4, 'latitude_2', drift_df['latitude_2'].values)
        drift.insert(5, 'longitude_2', drift_df['longitude_2'].values)
        
        # as with SAR drift filter, remove buoys where drift > 25 km/day
        speed_filter = (drift['speed_kmdy'] <= 25)
        drift = drift[speed_filter].copy()
        
        drift_results.append(drift)
    
    # Combine all buoys into a single DataFrame
    drift_all = pd.concat(drift_results, ignore_index=True)
    
    # round values
    drift_all['latitude_1'] = np.round(
        drift_all['latitude_1'], config['coordinate_precision']
    )
    drift_all['longitude_1'] = np.round(
        drift_all['longitude_1'], config['coordinate_precision']
    )
    drift_all['latitude_2']= np.round(
        drift_all['latitude_2'], config['coordinate_precision']
    )
    drift_all['longitude_2'] = np.round(
        drift_all['longitude_2'], config['coordinate_precision']
    )
    drift_all['X1'] = np.round(drift_all['X1'], config['coordinate_precision'])
    drift_all['Y1'] = np.round(drift_all['Y1'], config['coordinate_precision'])
    drift_all['X2'] = np.round(drift_all['X2'], config['coordinate_precision'])
    drift_all['Y2'] = np.round(drift_all['Y2'], config['coordinate_precision'])
    drift_all['dx'] = np.round(
        drift_all['dx'], config['displacement_precision']
    )
    drift_all['dy'] = np.round(
        drift_all['dy'], config['displacement_precision']
    )
    drift_all['distance'] = np.round(
        drift_all['distance'], config['displacement_precision']
    )
    drift_all['distance_geod']  = np.round(
        drift_all['distance_geod'], config['displacement_precision']
    )
    drift_all['bearing'] = np.round(
        drift_all['bearing'], config['bearing_precision']
    )
    drift_all['u']= np.round(drift_all['u'], config['displacement_precision'])
    drift_all['v']= np.round(drift_all['v'], config['displacement_precision'])
    drift_all['speed_ms'] = np.round(
        drift_all['speed_ms'], config['displacement_precision']
    )
    drift_all['speed_kmdy'] = np.round(
        drift_all['speed_kmdy'], config['displacement_precision']
    )

    # log skipped buoys
    if buoys_skipped:
        logger.info(f'Skipped {len(buoys_skipped)} buoy(s) |')
        for msg in buoys_skipped:
            logger.info(f'Buoy skipped | {msg}')

    
    return drift_all
    
    
def _get_layer_name(scene_id):
    """
    Derive a short GeoPackage layer name from a full scene_id string.
    
    Constructs a compact layer identifier from the sensor names and
    observation timestamps of both scenes in the pair, avoiding the
    full scene_id length which can exceed GeoPackage layer name limits.
    
    Args:
        scene_id (str): Full scene pair identifier in the format
            `<File1>_<File2>`, where each file follows the SAR gfilter
            naming convention:
            `<sensor>_<provider>_<YYYY>_<MM>_<DD>_<HH>_<MM>_<SS>_
            <julian_seconds>_<lon>_<lat>_<pol>_<C>`
    
    Returns:
        str: Layer name in the format:
            `drift_vectors_<sensor1>_<HH>_<MM>_<SS>_
            <sensor2>_<HH>_<MM>_<SS>`
            where `HH`, `MM`, `SS` are the hour, minute, and second
            components of each scene's acquisition time.
    
    Example:
        >>> _get_layer_name(
        ...     'RCM1_SHUB_2024_10_14_05_18_19_..._'
        ...     'RCM2_SHUB_2024_10_15_04_54_14_...'
        ... )
        
        unique layer name is:
        [sensor_1]_[hour_1]_[minute_1]_[second_1]_
        [sensor_2]_[hour_2]_[minute_2]_[secomd_2]
        --- or ---
        `drift_vectors_RCM1_05_18_19_RCM2_04_54_14`        
    """

    scene_id_parts = scene_id.split('_')
    layer_name = (
        f'drift_vectors_{scene_id_parts[0]}_'
        f'{scene_id_parts[5]}_{scene_id_parts[6]}_'
        f'{scene_id_parts[7]}_{scene_id_parts[13]}_'
        f'{scene_id_parts[18]}_{scene_id_parts[19]}_'
        f'{scene_id_parts[20]}'
    )

    return layer_name



def _update_interactive_html_files(config, epsg):
    """
    Write or refresh the interactive HTML index file and supporting web
    assets for the given EPSG output directory.

    Reads the `index.html` template, substitutes the EPSG label,
    description, available year range, and viewer path, then writes the
    result to `<file_server>/<epsg>/index.html`. Copies CSS, JS, image,
    and web font support folders from `meta_dir` to the file server. Then
    calls `_update_buoys_vectors` to write or refresh all per-day buoy
    JSON files for the level `03` data directory.

    This function is called once per EPSG for levels '00' and '03' during
    `process_level_output`, before the day loop begins.

    Args:
        config (dict): Configuration dictionary. Must include:
                - 'file_server' (str): Root output path.
                - 'html_index_template' (str): Path to the index.html
                  template file.
                - 'html_vector_template' (str): Filename of the vector
                  viewer HTML used to construct the viewer path constant
                  in the index.
                - 'webpage_folders' (list[str]): Folder names to copy
                  from `meta_dir` to the file server EPSG directory
                  (e.g. `['css', 'js', 'image', 'webfonts']`).
                - 'meta_dir' (str): Directory containing web support
                  folders and template files.
                - 'start_date' (date): Minimum date_start across all
                  input data; used to derive the start year for the
                  `AVAILABLE_YEARS` constant.
                - 'end_date' (date): Maximum date_start across all input
                  data; used to derive the end year.
                - 'buoy_drift' (pandas.DataFrame): Full buoy drift
                  DataFrame passed through to `_update_buoys_vectors`.
                - 'epsg' (int): Target EPSG code; used to construct the
                  buoy data directory path.
        epsg (int): EPSG code for the output directory (3413 or 6931).
            Controls which EPSG label and description are substituted
            into the template and which subdirectory receives the files.

    Returns:
        None

    Notes:
        - The following JavaScript constants are updated in the template
          via regex substitution: `EPSG_LABEL`, `EPSG_DESC`,
          `AVAILABLE_YEARS`, and `HTML_VIEWER_PATH`.
        - Web support folders at the destination are deleted and
          re-copied on each call to ensure stale assets are replaced.
        - Buoy JSON files are written for the level `03` data directory
          only: `<file_server>/<epsg>/Processing Level - 03 (PL03)/data/`.
    """
    
    import os
    import shutil
    import re

    EPSG_META = {
        3413: {
            'label': 'EPSG:3413',
            'desc':  'NSIDC Sea Ice Polar Stereographic North',
        },
        6931: {
            'label': 'EPSG:6931',
            'desc':  'NSIDC EASE-Grid 2.0 North',
        },
    }

    # year range
    start_year = config['start_date'].year
    end_year   = config['end_date'].year
    years      = list(range(start_year, end_year + 1))
    years_range   = '[' + ', '.join(str(y) for y in years) + ']'

    # Read template
    index_html_template_path = config['html_index_template']
    with open(index_html_template_path, 'r') as f:
        html_content = f.read()


    # update template content
    epsg_label = EPSG_META[epsg]['label']
    epsg_desc  = EPSG_META[epsg]['desc']

    html_content = re.sub(
        r"const EPSG_LABEL\s*=\s*'[^']*';",
        f"const EPSG_LABEL = '{epsg_label}';",
        html_content
    )
    html_content = re.sub(
        r"const EPSG_DESC\s*=\s*'[^']*';",
        f"const EPSG_DESC  = '{epsg_desc}';",
        html_content
    )
    html_content = re.sub(
        r"const AVAILABLE_YEARS\s*=\s*\[[^\]]*\];",
        f"const AVAILABLE_YEARS = {years_range};",
        html_content
    )
    viewer_path = (
        f"Processing%20Level%20-%2003%20(PL03)/"
        f"{os.path.basename(config['html_vector_template'])}"
    )
    html_content = re.sub(
        r"const HTML_VIEWER_PATH\s*=\s*'[^']*';",
        lambda _: f"const HTML_VIEWER_PATH = '{viewer_path}';",
        html_content
    )
    
    # create index.html
    index_html_path = os.path.join(
        config['file_server'], str(epsg), 'index.html'
    )
    os.makedirs(os.path.dirname(index_html_path), exist_ok=True)
    with open(index_html_path, 'w') as f:
        f.write(html_content)

    # copy css/js support folders
    for dir_name in config['webpage_folders']:
        src = os.path.join(config['meta_dir'], dir_name)
        dst = os.path.join(config['file_server'], str(epsg), dir_name)
        if os.path.isdir(src):
            if os.path.exists(dst):
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            
            
    # update buoy JSON files
    data_dir = os.path.join(
        config['file_server'],  str(config['epsg']),
        'Processing Level - 03 (PL03)', 'data'
    )
    _update_buoys_vectors(data_dir, config)
    

def _update_buoys_vectors(data_dir, config):
    """
    Write per-day buoy drift JSON files for all dates in the buoy drift
    DataFrame stored in config.

    Buoy observation data from the UW IABP dataset may be delayed relative
    to SAR drift data. This function iterates over all available buoy data
    and writes or overwrites a per-day JSON file for each date that has at
    least one observation. Running on the full DataFrame each time ensures
    delayed observations are always captured regardless of when they arrive.

    Args:
        data_dir (str): Directory path where per-day buoy JSON files are
            written. Each file is named `buoy_velocity_<YYYYMMDD>.json`.
        config (dict): Configuration dictionary. Must include:
                - 'buoy_drift' (pandas.DataFrame): Full buoy drift
                  DataFrame with columns:
                      - 'date' (str): Observation date ('YYYY-MM-DD').
                      - 'longitude_1', 'latitude_1' (float): Start
                        position (EPSG:4326, degrees).
                      - 'longitude_2', 'latitude_2' (float): End
                        position (EPSG:4326, degrees).
                      - 'speed_kmdy' (float): Drift speed (km day⁻¹).
                      - 'bearing' (float): Forward azimuth (degrees).

    Returns:
        None

    Notes:
        - Per-day JSON files are only written when at least one buoy
          observation exists for that date.
        - Each JSON payload follows the format:
            {
              'date1': 'YYYY-MM-DD',
              'date2': 'YYYY-MM-DD',
              'count': int,
              'vectors': [[lon1, lat1, lon2, lat2, speed_kmdy, bearing], ...]
            }
        - The JSON is written without indentation for compact output.
        - Existing files are overwritten unconditionally.
        - Progress is displayed via a tqdm progress bar keyed on unique
          dates in the DataFrame.
    """
    import os
    import json
    import logging
    from tqdm import tqdm

    logger = logging.getLogger('sar_drift_converter')
    os.makedirs(data_dir, exist_ok=True)

    df_buoy_drift = config['buoy_drift']
    groups = list(df_buoy_drift.groupby('date'))

    for date, group in tqdm(groups, desc='Writing buoy JSON files'):
        date_str = str(date).replace('-', '')

        vectors = [
            [
                float(row.longitude_1),
                float(row.latitude_1),
                float(row.longitude_2),
                float(row.latitude_2),
                float(row.speed_kmdy),
                float(row.bearing)
            ]
            for row in group.itertuples(index=False)
        ]

        if len(vectors) == 0:
            continue

        payload = {
            'date1':   str(date),
            'date2':   str(date),
            'count':   len(vectors),
            'vectors': vectors
        }

        json_path = os.path.join(
            data_dir, f'buoy_velocity_{date_str}.json'
        )
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(payload, f, separators=(',', ':'))

        logger.info(f'Updated buoy JSON {json_path}')
            
            
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
    
    Uses the mean resultant length R (the magnitude of the vector sum of
    unit vectors at each angle) to derive a dispersion measure analogous
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
 
        **Bearing z-score:** Computed using circular statistics -
        `arctan2(sin(Δ), cos(Δ))` normalizes the angular difference before
        dividing by circular standard deviation, correctly handling wrap-
        around near 0°/360°.
 
        **Iterative passes:** On each pass, the neighbor pool is restricted
        to current inliers only, preventing flagged vectors from inflating
        local statistics. Iteration stops early if the inlier count does not
        change between passes.
 
        **Performance:** Per-vector results are accumulated in plain Python
        lists during the inner loop and assigned to `out_df` in a single
        bulk `loc` operation per column per scene. This avoids the
        repeated copy-on-write overhead of row-by-row `df.at[...]` calls,
        which compounds significantly across large scenes and many days.
        The `tree.query` call for Mahalanobis neighbors is also separated
        from the `query_ball_point` result to prevent the kNN index array
        from overwriting the radius-based neighbor list mid-loop.
    """
    
    import numpy as np
    import logging
    import pandas as pd
    from scipy.spatial import cKDTree
    from sklearn.covariance import LedoitWolf
    from scipy.stats import chi2
    
    if config['level'] == '01':
        # no outlier detection required
        df['outlier_category'] = '-9'
        return df
    
 
    out_df = df.reset_index(drop=True).copy()
    
    radius_m = radius_km * 1000
    iter_prev_inliers = -1
    
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
 
        
        # base category set to all zeros
        base_cat = np.zeros(len(out_df), dtype=np.int8)
        mask_d = mask_b = mask_md = np.zeros(len(out_df), dtype=bool)
        mask_d_b = mask_md_d = np.zeros(len(out_df), dtype=bool)
        mask_md_b = mask_md_d_b = np.zeros(len(out_df), dtype=bool)
        
        # create neighbors for each scene
        for scene_id, scene_df in pool_df.groupby("scene", sort=False):
            xy = scene_df[["X1", "Y1"]].to_numpy()
            
            if len(xy) == 0:
                continue
            
            tree = cKDTree(xy)
            ball_neighbors = tree.query_ball_point(xy, r=radius_m)
            Xall = scene_df[
                ['sea_ice_x_displacement', 'sea_ice_y_displacement']
            ].to_numpy()
 
            # pre-compute kNN indices once per scene (avoids overwriting
            # ball_neighbors mid-loop in the original row-by-row approach)
            k_md = min(md_neighbors + 1, len(scene_df))
            _, knn_indices = tree.query(xy, k=k_md)
 
            # accumulate per-row results in lists
            sd_neighbor_indices_list = []
            sd_neighbor_count_list = []
            distance_z_score_list = []
            bearing_z_score_list = []
            md_neighbor_indices_list = []
            md_neighbor_count_list = []
            mahal_sq_list = []
            thr_sq_list = []
            mahal_outlier_flag_list = []
 
            for local_idx, local_neighbors in enumerate(ball_neighbors):
                
                # drop self
                neigh_idxs = [
                    j for j in local_neighbors if j != local_idx
                ]
                
                target_out_idx = scene_df.index[local_idx]
                
                if len(neigh_idxs) == 0:
                    sd_neighbor_indices_list.append([])
                    sd_neighbor_count_list.append(0)
                    distance_z_score_list.append(np.nan)
                    bearing_z_score_list.append(np.nan)
                    md_neighbor_indices_list.append([])
                    md_neighbor_count_list.append(0)
                    mahal_sq_list.append(np.nan)
                    thr_sq_list.append(np.nan)
                    mahal_outlier_flag_list.append(False)
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
 
                sd_neighbor_indices_list.append(neigh_out_idx)
                sd_neighbor_count_list.append(len(neigh_out_idx))
                distance_z_score_list.append(np.round(dist_z_score, 3))
                bearing_z_score_list.append(np.round(bear_z_score, 3))
                
 
                # Mahalanobis distance
                # use pre-computed knn_indices to avoid overwriting ball
                # neighbor results (all_neighbors) mid-loop
                md_neigh_idxs = [
                    j for j in knn_indices[local_idx].tolist()
                    if j != local_idx
                ]
                
            
                # Mahalanobis on neighbors
                x = Xall[local_idx, :] # target vector
                Xn = Xall[md_neigh_idxs, :] # neighbor matrix
                
                # Need enough neighbors to estimate covariance robustly
                p = Xn.shape[1] # degrees of freedom
                if len(md_neigh_idxs) < max(2 * p + 1, md_neighbors) or \
                    k_md < md_neighbors + 1:
                    mahal_sq = np.nan
                    thr_sq   = np.nan
                else:
                    # standardize data
                    mu = Xn.mean(axis=0)
                    sd = Xn.std(axis=0)
                    sd[sd == 0] = 1.0
                    Xn_z = (Xn - mu) / sd
                    x_z = (x - mu) / sd
                    
                    if np.linalg.matrix_rank(Xn_z) < p:
                        mahal_sq = np.nan
                        thr_sq   = np.nan
                    else:
                        # standard covariance measurement
                        # mcd = MinCovDet().fit(Xn_z)
                        # squared distance
                        # mahal_sq = mcd.mahalanobis([x_z])[0]
                        # better for small samples or the covariance
                        # is ill-conditioned.
                        lw = LedoitWolf().fit(Xn_z)
                        # squared distance
                        mahal_sq = lw.mahalanobis([x_z])[0]
                        # 99 strict threshold
                        alpha  = chi_square_level 
                        # squared-distance threshold
                        thr_sq = chi2.ppf(alpha, df=p) 
                
                # store neighbors as out_df indices
                md_neigh_out_idx = [
                    int(scene_df.index[j]) for j in md_neigh_idxs
                ]
                md_neigh_out_idx = [
                    i for i in md_neigh_out_idx if i != target_out_idx
                ]
 
                md_neighbor_indices_list.append(md_neigh_out_idx)
                md_neighbor_count_list.append(len(md_neigh_out_idx))
                mahal_sq_list.append(mahal_sq)
                thr_sq_list.append(thr_sq)
                mahal_outlier_flag_list.append(
                    False if np.isnan(mahal_sq)
                    else bool(mahal_sq > thr_sq)
                )
 
            # bulk-assign all per-row results to data frame
            idx = scene_df.index
            out_df.loc[idx, "sd_neighbor_indices"] = pd.array(
                sd_neighbor_indices_list, dtype=object
            )
            out_df.loc[idx, "sd_neighbor_count"] = sd_neighbor_count_list
            out_df.loc[idx, "distance_z_score"] = distance_z_score_list
            out_df.loc[idx, "bearing_z_score"] = bearing_z_score_list
            out_df.loc[idx, "md_neighbor_indices"] = pd.array(
                md_neighbor_indices_list, dtype=object
            )
            out_df.loc[idx, "md_neighbor_count"] = md_neighbor_count_list
            out_df.loc[idx, "mahal_sq"] = mahal_sq_list
            out_df.loc[idx, "thr_sq"] = thr_sq_list
            out_df.loc[idx, "mahal_outlier_flag"] = mahal_outlier_flag_list
 
            
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
        
        
        # stability check
        if n_inliers == iter_prev_inliers:
            break
        iter_prev_inliers = n_inliers
        
    
    return out_df


#=========
# Data I/O
#=========

def read_sar_drift_data_file(input_file, config):
    """
    Read and preprocess a SAR ice-drift text data file into a standardized
    raw DataFrame.

    Loads a SAR drift data file (CSV-like text) using parsing rules provided
    in `config`, cleans column names, converts Julian-second timestamps to
    human-readable datetime strings, computes observation duration, extracts
    sensor and scene identifiers, renames geographic coordinate columns for
    consistency with downstream output naming, and reduces the DataFrame to
    only the columns needed for downstream processing.

    Projection-dependent quantities (projected coordinates, displacement,
    velocity, speed, bearing) are NOT computed here. They depend on a target
    EPSG and are applied separately by `_apply_projection` after all files
    have been read and combined. This separation allows the expensive file
    I/O step to run exactly once regardless of how many target projections
    are required.

    Processing steps:
        1. Detect the header row automatically via `_detect_skip_rows`,
           which scans the first 10 lines for the row containing 'File1'
           and 'File2'.
        2. Read the file with `pandas.read_csv()` using the detected row
           offset and the delimiter from `config`.
        3. Strip whitespace from column names.
        4. Convert Julian seconds timestamps (`Time1_JS`, `Time2_JS`) to
           human-readable datetime strings (`date_start`, `date_end`).
        5. Compute observation duration in seconds (`duration`).
        6. Extract sensor identifiers from `File1`/`File2` into `sensor1`/
           `sensor2` and construct `scene_id`.
        7. Rename geographic coordinate columns:
               Lat1 → latitude_1,  Lon1 → longitude_1
               Lat2 → latitude_2,  Lon2 → longitude_2
        8. Reduce the DataFrame to only the columns needed for downstream
           processing.

    Args:
        input_file (str or pathlib.Path): Path to the SAR drift data file
                                          to read.
        config (dict): Parsing configuration. Expected keys:
            - 'delimiter' (str): Field delimiter passed to `pd.read_csv`.

    Returns:
        pandas.DataFrame: Cleaned raw SAR drift DataFrame containing the
            following columns:

            Renamed geographic coordinates (EPSG:4326, degrees):
                - 'latitude_1'  (float): Starting latitude  (from Lat1).
                - 'longitude_1' (float): Starting longitude (from Lon1).
                - 'latitude_2'  (float): Ending latitude    (from Lat2).
                - 'longitude_2' (float): Ending longitude   (from Lon2).

            Derived timestamps and duration:
                - 'date_start' (str): Start datetime string
                  ('%Y-%m-%d %H:%M:%S'), converted from Time1_JS.
                - 'date_end'   (str): End datetime string
                  ('%Y-%m-%d %H:%M:%S'), converted from Time2_JS.
                - 'duration' (float): Observation duration in seconds
                  (Time2_JS − Time1_JS).

            Sensor and scene identifiers:
                - 'sensor1'  (str): Satellite identifier from File1
                                    (prefix before first underscore).
                - 'sensor2'  (str): Satellite identifier from File2.
                - 'scene_id' (str): File1 and File2 joined by underscore.

            Scene pair identifiers and correlation scores:
                - 'File1', 'File2' (str): Raw scene pair filenames.
                - 'Maxcorr1', 'Maxcorr2' (float): Cross-correlation scores
                  used for scene-level quality filtering downstream.

    Notes:
        - SAR time fields `Time1_JS` and `Time2_JS` are seconds since
          2000-01-01 00:00:00 UTC.
        - Header row detection is performed automatically by
          `_detect_skip_rows`. No configuration key or argument is required
          to control this - the function always scans the file to locate
          the header.
        - Projection-dependent columns (X1, Y1, X2, Y2,
          sea_ice_x_displacement, sea_ice_y_displacement, u, v,
          sea_ice_speed, sea_ice_speed_kmdy,
          direction_of_sea_ice_displacement, distance, distance_geod)
          are not present in the returned DataFrame. Call
          `_apply_projection(df, epsg, config)` to add them after all
          files have been combined.
    """

    import numpy as np
    import pandas as pd
    from datetime import datetime, timedelta

    skip_rows = _detect_skip_rows(input_file)

    # read the SAR drift data file
    df = pd.read_csv(
        input_file, delimiter=config['delimiter'],
        header=0, engine='c', skiprows=skip_rows
    )
    df.columns = df.columns.str.strip()

    # convert Julian seconds (epoch: 2000-01-01) to datetime strings
    base_time = datetime(2000, 1, 1)
    df['date_start'] = df['Time1_JS'].apply(
        lambda x: base_time + timedelta(seconds=x)
    )
    df['date_start'] = df['date_start'].dt.strftime('%Y-%m-%d %H:%M:%S')
    df['date_end'] = df['Time2_JS'].apply(
        lambda x: base_time + timedelta(seconds=x)
    )
    df['date_end'] = df['date_end'].dt.strftime('%Y-%m-%d %H:%M:%S')

    # observation duration in seconds
    df['duration'] = df['Time2_JS'] - df['Time1_JS']

    # sensor and scene identifiers
    df['sensor1']  = df['File1'].str.partition('_')[0]
    df['sensor2']  = df['File2'].str.partition('_')[0]
    df['scene_id'] = df['File1'] + '_' + df['File2']


    # longitudes appear mixed - standardize -180 to 180
    df['Lon1'] = np.where(df['Lon1'] > 180, df['Lon1'] - 360, df['Lon1'])
    df['Lon2'] = np.where(df['Lon2'] > 180, df['Lon2'] - 360, df['Lon2'])
    
    df['Lon1'] = round(df['Lon1'], config['coordinate_precision'])
    df['Lat1'] = round(df['Lat1'], config['coordinate_precision'])
    df['Lon2'] = round(df['Lon2'], config['coordinate_precision'])
    df['Lat2'] = round(df['Lat2'], config['coordinate_precision'])

    # rename geographic coordinate columns
    df.rename(columns={
        'Lat1': 'latitude_1',
        'Lon1': 'longitude_1',
        'Lat2': 'latitude_2',
        'Lon2': 'longitude_2'
    }, inplace=True)

    # reduce to only columns needed downstream
    needed_cols = [
        'File1', 'File2', 'Maxcorr1', 'Maxcorr2',
        'longitude_1', 'latitude_1', 'longitude_2', 'latitude_2',
        'date_start', 'date_end', 'duration',
        'sensor1', 'sensor2', 'scene_id'
    ]
    df = df[needed_cols]

    return df


def combine_into_dataframe(files, config):
    """
    Read a list of SAR drift gfilter files into a single combined raw
    DataFrame using parallel file reads across multiple CPU cores.
 
    Iterates over the provided file paths, skipping any 75 km files
    encountered directly (they are resolved automatically from their paired
    50 km entry). For each 50 km file, checks whether a corresponding 75 km
    file exists and, if so, reads the 75 km file in its place. File reads
    are parallelized using ProcessPoolExecutor to reduce wall-clock time on
    multi-core machines. All per-file DataFrames are concatenated into a
    single raw DataFrame with datetime columns parsed once after combining.
 
    The returned DataFrame contains only EPSG-independent columns. Projection-
    dependent columns (X1, Y1, X2, Y2, displacement, velocity, speed,
    bearing) are NOT added here. Call `util._apply_projection(df_raw, epsg,
    config)` separately for each target EPSG after this function returns.
    This design allows the expensive parallel file I/O to run exactly once
    regardless of how many EPSG projections are required.
 
    Args:
        files (list[str]): Paths to candidate gfilter input files, typically
            glob-matched from `config['sar_drift_directory']`. Files with
            `_0075000m_` in their path are silently skipped; they are only
            read when resolved from a paired 50 km entry.
        config (dict): Configuration dictionary. Must include:
                - `delimiter` (str): Field delimiter passed to
                  `util.read_sar_drift_data_file`.
                - `max_workers` (int, optional): Maximum number of worker
                  processes for parallel file reads. Defaults to
                  min(32, os.cpu_count()) if not set.
 
    Returns:
        pandas.DataFrame: Combined raw DataFrame of all successfully read
            drift observations. Contains only EPSG-independent columns as
            produced by `util.read_sar_drift_data_file`:
                - `File1`, `File2` (str): Scene pair filenames.
                - `Maxcorr1`, `Maxcorr2` (float): Cross-correlation scores.
                - `latitude_1`, `longitude_1` (float): Start position
                  (EPSG:4326, degrees).
                - `latitude_2`, `longitude_2` (float): End position
                  (EPSG:4326, degrees).
                - `date_start` (pandas.Timestamp): Parsed start datetime.
                - `date_end` (pandas.Timestamp): Parsed end datetime.
                - `duration` (float): Observation duration in seconds.
                - `sensor1`, `sensor2` (str): Satellite identifiers.
                - `scene_id` (str): `File1`_`File2`.
                - `_use_75km` (bool): True if the 75 km file was read in
                  place of the 50 km file for this observation's scene.
                - `_source_file` (str): Basename of the file actually read.
 
    Raises:
        Exception: Re-raises any exception encountered during file reading
            via the worker function `_read_gfilter_file`, causing the
            executor to terminate and propagating the error to the caller.
            Processing halts immediately on the first file read failure.
 
    Notes:
        - 75 km files are identified by the substring `_0075000m_` in the
          file path. Any such file appearing directly in `files` is skipped
          and counted as a candidate but not read, as it will be resolved
          from its paired 50 km entry.
        - The 75 km counterpart of a 50 km file is derived by replacing
          `_0050000m_` with `_0075000m_` in the normalized path. If the
          resulting path is unchanged or the 75 km path does not exist on
          disk, the original 50 km path is read instead.
        - File extensions containing an underscore suffix (e.g. .txt_0)
          are normalized by truncating at the first underscore before the
          75 km path substitution is attempted.
        - Header row position is detected automatically per file by
          `_detect_skip_rows` inside `util.read_sar_drift_data_file`. No
          configuration key is required for this.
        - Date columns are parsed to pandas Timestamps once after all files
          are concatenated, rather than per-file, for efficiency.
        - Worker count defaults to min(32, os.cpu_count()) and can be
          overridden via config['max_workers'].
        - On Windows the ProcessPoolExecutor uses the `spawn` start method.
          The entry point must be protected by `if __name__ == "__main__":`
          to prevent recursive worker spawning.
    """

    import os
    import sys
    import logging
    import pandas as pd
    from tqdm import tqdm
    from concurrent.futures import ProcessPoolExecutor

    logger = logging.getLogger('sar_drift_converter')

    candidate_files = [f for f in files if '_0075000m_' not in f]
    max_workers = min(32, os.cpu_count())

    logger.info(
        f"Reading {len(candidate_files)} gfilter files "
        f"using {max_workers} workers"
    )
    files_75km = len(files) - len(candidate_files)
    logger.info(
        f"{files_75km} 75km files identified for substitution "
        f"(will replace paired 50km files where available) | "
        f"Difference of candidate files and files read for processing"
    )

    args = [(f, config) for f in candidate_files]
    all_dfs = []
    failed = 0


    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        results = list(tqdm(
            executor.map(_read_gfilter_file, args),
            total=len(args),
            desc='Reading gfilter files...',
            unit='file',
            file=sys.stdout,
            dynamic_ncols=True
        ))

    all_dfs = [r for r in results if r is not None]
    failed = len(results) - len(all_dfs)

    if failed:
        logger.warning(f"{failed} file(s) failed to read and were skipped")
        

    print('Combining all files into one Data Frame...')
    df_all = pd.concat(all_dfs, ignore_index=True)

    df_all['date_start'] = pd.to_datetime(
        df_all['date_start'], format='%Y-%m-%d %H:%M:%S'
    )
    df_all['date_end'] = pd.to_datetime(
        df_all['date_end'], format='%Y-%m-%d %H:%M:%S'
    )

    logger.info(
        f"Combined: {df_all.shape[0]} rows from {len(all_dfs)} files "
        f"({failed} failed)"
    )

    return df_all
    

def filter_input_data(df_all, config):
    """
    Apply scene-level and row-level quality filters to the combined drift
    DataFrame.
    
    Filtering behavior is controlled by `config['level']`. For levels '02'
    and '03', each File1/File2 scene pair is evaluated independently with a
    sequence of per-row drops and scene-level rejection checks. Scenes that
    fail a rejection check are discarded entirely; rows that fail a per-row
    check are dropped from their scene. For all other levels the DataFrame is
    returned unchanged, except level '00' which additionally saves the
    unfiltered combined CSV to disk.
    
    Args:
        df_all (pandas.DataFrame): Combined drift observations from all input
            files, as produced by `combine_into_dataframe`. Expected columns:
                - 'File1', 'File2' (str): Scene pair identifiers; used to
                  group observations into scenes.
                - 'direction_of_sea_ice_displacement' (float): Forward azimuth
                  (degrees); rows with a value of 0 are dropped.
                - 'sea_ice_speed' (float): Drift speed (m s⁻¹); rows with a
                  value of 0 or above the speed threshold are dropped.
                - 'Maxcorr1', 'Maxcorr2' (float): Cross-correlation scores;
                  used for the scene-level 60% check and per-row validity
                  drop.
                - '_use_75km' (bool): Whether the 75 km file was used for
                  this scene; controls the speed anomaly threshold (35.0 m s⁻¹
                  for 75 km files, 25.0 m s⁻¹ for 50 km files).
                - 'date_start', 'date_end' (str): Observation timestamps;
                  re-parsed to pandas datetimes after filtering.
        config (dict): Configuration dictionary. Must include:
                - 'level' (str): Processing level; filtering is only applied
                                 for levels '02' and '03'. Level '00' triggers
                                 an unfiltered CSV save. Levels '01' and above
                                 '03' return `df_all` unchanged.
                - 'ignore_vector_threshold' (int): Minimum number of rows a
                  scene must retain after all per-row drops to be accepted.
                - 'filtered_data_dir' (str): Output directory for the
                  unfiltered combined CSV (level '00' only).
    
    Returns:
        pandas.DataFrame: Filtered DataFrame containing only accepted scenes
            and valid rows, with 'date_start' and 'date_end' re-parsed as
            pandas Timestamps. For levels other than '02' and '03', the
            original DataFrame is returned unchanged.
    
    Notes:
        **Per-row drops (levels '02' and '03', applied in order):**

        1. Remove rows where `direction_of_sea_ice_displacement == 0`
           AND `sea_ice_speed == 0` simultaneously. A zero bearing alone
           or zero speed alone does not trigger a drop; both must be zero.
        2. Remove rows where `sea_ice_speed >= 25.0 m s⁻¹` (50 km files)
           or `>= 35.0 m s⁻¹` (75 km files).
        3. Remove rows where `Maxcorr2 <= Maxcorr1`.

        **Scene-level rejection (levels '02' and '03', entire scene
        discarded if):**

        1. Fewer than 60% of rows have `Maxcorr2 > Maxcorr1`, evaluated
           after the bearing/speed validity drop but before the per-row
           Maxcorr drop.
        2. Remaining row count falls below `ignore_vector_threshold` after
           all per-row drops.

        - Each filter step is logged individually, reporting rows dropped
          and the scene identifier. Rejected scenes are logged at WARNING
          level; accepted scenes and per-row drops at INFO level.
        - The 60% Maxcorr check precedes the per-row Maxcorr drop
          intentionally: a scene where the majority of vectors have poor
          correlation is rejected outright rather than thinned.
    """
    
    import os
    import logging
    import pandas as pd
    from tqdm import tqdm

    # log activity
    logger = logging.getLogger('sar_drift_converter')
    
    
    if config['level'] in ['02', '03']:
        accepted = []
        scenes = list(df_all.groupby(['File1', 'File2']))
        total_scenes = len(scenes)
        chunks = max(1, total_scenes // 20)
        for (file1, file2), df_scene in tqdm(
                scenes, desc='Filtering scenes...',
                total=total_scenes,
                miniters=chunks,
                mininterval=0,
                unit='scene'
            ):
            scene_id = f"{file1}_{file2}"
            use_75km = df_scene['_use_75km'].iloc[0]
            initial_row_size = df_scene.shape[0]
    
            # remove invalid bearings and speeds
            df_scene = df_scene[
                ~(
                    (df_scene['direction_of_sea_ice_displacement'] == 0) &
                    (df_scene['sea_ice_speed'] == 0)
                )
            ]
            if initial_row_size != df_scene.shape[0]:
                logger.info(
                    f"{scene_id} | after bearing/speed validity: "
                    f"{df_scene.shape[0]} (dropped "
                    f"{initial_row_size - df_scene.shape[0]})"
                )
                
            # remove invalid speeds
            speed_thresh = 35.0 if use_75km else 25.0
            row_count_before = df_scene.shape[0]
            df_scene = df_scene[df_scene['sea_ice_speed'] < speed_thresh]
            if row_count_before != df_scene.shape[0]:
                logger.info(
                    f"{scene_id} | after speed filter "
                    f"(sea_ice_speed >= {speed_thresh}): {df_scene.shape[0]} "
                    f"(dropped {row_count_before - df_scene.shape[0]})"
                )
    
            # reject scene if < 60% have MaxCorr2 > MaxCorr1
            pct_correct = (
                df_scene['Maxcorr2'] > df_scene['Maxcorr1']
            ).mean() * 100
            if pct_correct < 60:
                logger.warning(
                    f"Reject scene: {scene_id} | "
                    f"pct_correct={pct_correct:.1f}% (<60%)"
                )
                continue
    
            # remove rows where MaxCorr2 <= MaxCorr1
            row_count_before = df_scene.shape[0]
            df_scene = df_scene[df_scene['Maxcorr2'] > df_scene['Maxcorr1']]
            if row_count_before != df_scene.shape[0]:
                logger.info(
                    f"{scene_id} | after Maxcorr2 > Maxcorr1: "
                    f"{df_scene.shape[0]} (dropped "
                    f"{row_count_before - df_scene.shape[0]})"
                )
    
            # reject scene if too few observations
            if df_scene.shape[0] < config['ignore_vector_threshold']:
                logger.warning(
                    f"Reject scene: {scene_id} | "
                    f"only {df_scene.shape[0]} observations "
                    f"(threshold={config['ignore_vector_threshold']})"
                )
                continue
    
            logger.info(
                f"Accepted scene: {scene_id} | final rows={df_scene.shape[0]}"
            )
            accepted.append(df_scene)
            
    
        print('Updating Data Frame with filtered data...')
        df_all = pd.concat(accepted, ignore_index=True)
        df_all['date_start'] = pd.to_datetime(
            df_all['date_start'],
            format='%Y-%m-%d %H:%M:%S'
        )
        df_all['date_end'] = pd.to_datetime(
            df_all['date_end'],
            format='%Y-%m-%d %H:%M:%S'
        )
        logger.info(
            f"After filtering: {df_all.shape[0]} rows across "
            f"{len(accepted)} scenes"
        )
    
    
    # save filtered combined CSV
    if config['level'] == "00":
        print('Saving combined Data Frame...')
        df_all.to_csv(
            os.path.join(
                config['filtered_data_dir'],'filtered_combined.csv'
            ),
            index=False
        )    
    
    return df_all


def _copy_to_gdrive(config):
    import subprocess
    import logging
    logger = logging.getLogger('sar_drift_converter')

    service_account = config.get('gdrive_service_account')
    folder_id = config.get('gdrive_folder_id')
    if not service_account or not folder_id:
        return

    logger.info('Copying output files to Google Drive...')
    result = subprocess.run(
        [
            'rclone', 'copy',
            config['file_server'],
            f':drive,service_account_file={service_account},'
            f'root_folder_id={folder_id}:',
            '--transfers', '8'
        ],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        logger.error(f'rclone copy failed: {result.stderr}')
    else:
        logger.info('Google Drive copy complete')
        
        

###############
# Create Output
###############

def create_netcdf(df, nc_path, config, template_ds, multi_layered=False):
    """
    Create a gridded NetCDF sea-ice drift product from point/vector
    observations. Supports both single-scene and multi-scene (daily)
    output in one unified function.

    Maps input drift vectors onto the NSIDC 12.5 km polar stereographic
    grid, populates a NetCDF dataset using attributes from a CDL metadata
    template, crops the output to the spatial extent of all valid
    observations with padding, and writes the result to disk with
    compression.

    For single-scene output (`multi_layered=False`), the DataFrame is
    treated as one scene and written as a single time layer. For daily
    output (`multi_layered=True`), the DataFrame is grouped by `scene_id`
    and each group is written as a separate time layer on the shared grid.
    In both cases the output is cropped to the bounding box of all finite
    `sea_ice_speed` values across the full DataFrame.

    Args:
        df (pandas.DataFrame): Input drift observations. For scene output,
            contains rows for one scene pair. For daily output, contains
            rows for all scene pairs in the day. Expected columns:
                - 'scene_id' (str): Scene pair identifier; used as
                  `layer_id` coordinate. For multi-layered output, rows
                  are grouped by this column.
                - 'date_start' (datetime-like): Start timestamp.
                - 'date_end' (datetime-like): End timestamp.
                - 'longitude_1', 'latitude_1' (float): Start position
                  (EPSG:4326); used to locate grid cells.
                - 'sea_ice_speed' (float): Drift speed (m s⁻¹).
                - 'sea_ice_x_displacement' (float): X displacement (m).
                - 'sea_ice_y_displacement' (float): Y displacement (m).
                - 'direction_of_sea_ice_displacement' (float): Forward
                  azimuth (degrees).
                - 'outlier_category' (str): Two-digit outlier code. For
                  level '03', only rows with values '00' or '01' are
                  retained and recoded to -1 before writing.
                - 'Maxcorr1', 'Maxcorr2' (float): Cross-correlation
                  scores; used for `measurement_error` flag in levels
                  '00'/'01'.
                - '_use_75km' (bool): Whether the 75 km file was used;
                  controls speed threshold for `speed_error` flag. For
                  multi-layered output this is evaluated per scene group
                  since different scenes may differ.
        base_name (str): Base filename (without extension). Output is
            written to `<config['nc_dir']>/<base_name>.nc`.
        config (dict): Configuration dictionary. Must include:
                - 'nc_dir' (str): Output directory.
                - 'level' (str): Processing level ('00'–'03'); controls
                  inlier filtering, error flag computation, and fill
                  value assignment.
                - 'epsg' (int): EPSG code used upstream for displacement
                  computation. Does not affect output grid, which is
                  always the NSIDC 12.5 km polar stereographic grid.
        template_ds (xarray.Dataset): Template dataset providing the
            target grid coordinate arrays and dimensions.
        multi_layered (bool): If False (default), writes a single time
            layer for the scene. If True, groups `df` by `scene_id` and
            writes one time layer per group for daily output.

    Returns:
        str: Path to the written NetCDF file. Returns None early if
            level is '03' and no rows survive the inlier filter.

    Notes:
        - The output grid is always the NSIDC 12.5 km polar stereographic
          grid, regardless of `config['epsg']`.
        - `time` coordinate uses minimum `date_start` in Julian seconds
          (seconds since 2000-01-01).
        - `time_bnds` spans [min(date_start), max(date_end)] per time
          layer.
        - `layer_id` is set to `scene_id` for each time layer.
        - The bounding box crop uses all finite `sea_ice_speed` values
          across the full grid, regardless of whether output is single-
          scene or multi-scene. A 4-cell pad is applied on each side.
        - Duplicate (i, j) assignments within a time layer are detected
          and logged; the last observation written wins.
        - All int16 flag variables use -9 as `_FillValue`.
        - For level '03', `outlier_category` is recoded to -1 for all
          written observations.
        - For `multi_layered=True`, `speed_error` threshold is evaluated
          per scene group using that group's `_use_75km` value, since
          scenes within a day may differ.
    """

    import numpy as np
    import pandas as pd
    from datetime import datetime
    import xarray as xr
    import logging

    logger = logging.getLogger('sar_drift_converter')


    # standardize timestamps
    df_copy = df.copy()
    df_copy['date_start'] = pd.to_datetime(df_copy['date_start'])
    df_copy['date_end'] = pd.to_datetime(df_copy['date_end'])
    


    # for level 03, retain only inlier vectors and recode outlier_category
    if config['level'] == '03':
        outlier_filter = df_copy['outlier_category'].isin(['00', '01'])
        df_copy = df_copy[outlier_filter].copy()
        df_copy['outlier_category'] = -1
        if df_copy.shape[0] == 0:
            logger.info('All outliers found. No data to process.')
            return None


    # compute error flags per row for levels 00/01
    if config['level'] in ['00', '01']:
        df_copy['bearing_error'] = (
            (df_copy['direction_of_sea_ice_displacement'] == 0) &
            (df_copy['sea_ice_speed'] == 0)
        ).astype(int)

        # speed threshold varies per scene - apply per scene_id group
        for scene_id, grp in df_copy.groupby('scene_id'):
            speed_thresh = 35.0 if grp['_use_75km'].iloc[0] else 25.0
            speed_error = (~(grp['sea_ice_speed'] < speed_thresh)).astype(int)
            df_copy.loc[grp.index, 'speed_error'] = speed_error

        df_copy['measurement_error'] = (
            df_copy['Maxcorr1'] > df_copy['Maxcorr2']
        ).astype(int)
        
    else:
        # for levels 2 and 3, the bad vectors have already been removed
        df_copy['bearing_error'] = 0
        df_copy['speed_error'] = 0
        df_copy['measurement_error'] = 0


    # map all observations to (i, j) grid indices
    lons = df_copy["longitude_1"].to_numpy(dtype=float)
    lats = df_copy["latitude_1"].to_numpy(dtype=float)
    lons_normalized = np.where(lons < 0, lons + 360, lons)
    i_all, j_all = _polar_lonlat_to_ij(
        lons_normalized, lats, grid_size=12.5, hemisphere="north"
    )
    i_all = np.asarray(i_all, dtype=np.int64)
    j_all = np.asarray(j_all, dtype=np.int64)
    df_copy = df_copy.reset_index(drop=True)
    df_copy['grid_i'] = i_all
    df_copy['grid_j'] = j_all


    # determine scene groups and time layer count
    epoch = pd.Timestamp('2000-01-01')
    x_coords = template_ds['x'].values
    y_coords = template_ds['y'].values

    if multi_layered:
        scene_groups = [
            (sid, grp.reset_index(drop=True))
            for sid, grp in df_copy.groupby('scene_id', sort=True)
        ]
    else:
        scene_groups = [(df_copy['scene_id'].iloc[0], df_copy)]

    n_time = len(scene_groups)
    grid_shape = (n_time, template_ds.sizes['y'], template_ds.sizes['x'])

    # build time arrays across all scene groups
    time_array = np.zeros(n_time, dtype='float64')
    time_bounds = np.zeros((n_time, 2), dtype='float64')
    layer_id_list = []

    for t_idx, (scene_id, grp) in enumerate(scene_groups):
        t_sec = float((grp['date_start'].min() - epoch).total_seconds())
        t_end = float((grp['date_end'].max() - epoch).total_seconds())
        time_array[t_idx] = t_sec
        time_bounds[t_idx, 0] = t_sec
        time_bounds[t_idx, 1] = t_end
        layer_id_list.append(_get_layer_name(scene_id))

    min_time = df_copy['date_start'].min()
    max_time = df_copy['date_end'].max()


    # create NetCDF file
    netcdf_grid = None
    try:
        # load CDL metadata attributes
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

        # build empty grid
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
                "time":     ("time", time_array, time_attrs),
                "layer_id": ("time", np.array(layer_id_list), layer_id_attrs),
                "nv":       [0, 1],
                "x":        ("x", x_coords, x_attrs),
                "y":        ("y", y_coords, y_attrs)
            },
            attrs=global_attrs
        )

        netcdf_grid.attrs['date_created'] = (
            datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        )
        netcdf_grid.attrs['time_coverage_start'] = (
            min_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        )
        netcdf_grid.attrs['time_coverage_end'] = (
            max_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        )

        # populate grid (one time layer per scene group)
        for t_idx, (scene_id, grp) in enumerate(scene_groups):
            # seen_key = set()
            for row in grp.itertuples(index=False):
                ix = int(row.grid_i)
                iy = int(row.grid_j)
                # index_key = (ix, iy)
                # if index_key in seen_key:
                #     logger.info(
                #         f'{scene_id} | Duplicate entry at ({ix}, {iy})'
                #     )
                # seen_key.add(index_key)

                netcdf_grid["sea_ice_speed"].values[
                    t_idx, iy, ix] = np.float32(row.sea_ice_speed)
                netcdf_grid["sea_ice_x_displacement"].values[
                    t_idx, iy, ix] = np.float32(row.sea_ice_x_displacement)
                netcdf_grid["sea_ice_y_displacement"].values[
                    t_idx, iy, ix] = np.float32(row.sea_ice_y_displacement)
                netcdf_grid["direction_of_sea_ice_displacement"].values[
                    t_idx, iy, ix] = np.float32(
                        row.direction_of_sea_ice_displacement)
                netcdf_grid["outlier_category"].values[
                    t_idx, iy, ix] = np.int16(row.outlier_category)
                netcdf_grid["bearing_error"].values[
                    t_idx, iy, ix] = np.int16(row.bearing_error)
                netcdf_grid["speed_error"].values[
                    t_idx, iy, ix] = np.int16(row.speed_error)
                netcdf_grid["measurement_error"].values[
                    t_idx, iy, ix] = np.int16(row.measurement_error)


        # crop to bounding box of all finite speed values across all layers
        data_mask = np.any(
            np.isfinite(netcdf_grid["sea_ice_speed"].values), axis=0
        )
        if np.any(data_mask):
            filled_y, filled_x = np.where(data_mask)
            pad_cells = 4
            y_start = max(0, int(filled_y.min()) - pad_cells)
            y_end   = min(
                netcdf_grid.sizes["y"] - 1, int(filled_y.max()) + pad_cells
            )
            x_start = max(0, int(filled_x.min()) - pad_cells)
            x_end   = min(
                netcdf_grid.sizes["x"] - 1, int(filled_x.max()) + pad_cells
            )
            netcdf_grid = netcdf_grid.isel(
                y=slice(y_start, y_end + 1),
                x=slice(x_start, x_end + 1)
            )

        # save to NetCDF
        netcdf_grid.to_netcdf(
            nc_path, mode='w',
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
                'time_bnds':   {'dtype': 'float64'},
                'spatial_ref': {'dtype': 'int32'}
            }
        )

    
        logger.info(f'Created NetCDF {nc_path}')

    finally:
        if netcdf_grid is not None:
            netcdf_grid.close()
            del netcdf_grid


def create_shape_package(df, gpkg_path, config):
    """
    Create a GeoPackage containing drift line vectors for SAR drift data.

    Builds LineString geometries from projected start and end coordinates
    (EPSG:`config['epsg']`) and writes them to a GeoPackage. For levels
    '00' and '02', one layer is written per scene pair, named
    `drift_vectors_<scene_id>`. For level '03', a single `drift_vectors`
    layer is written containing only inlier vectors (outlier_category '00'
    or '01'), with outlier_category recoded to -1. A QML style file is
    embedded directly into the GeoPackage's `layer_styles` table for each
    layer for automatic styling when opened in QGIS.

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
                    - 'duration' (float): Observation duration (s).
                Sensor identifiers:
                    - 'sensor1', 'sensor2' (str): Satellite/sensor IDs.
                Measurement variables:
                    - 'sea_ice_x_displacement' (float): X displacement (m).
                    - 'sea_ice_y_displacement' (float): Y displacement (m).
                    - 'u' (float): X velocity component (m s⁻¹).
                    - 'v' (float): Y velocity component (m s⁻¹).
                    - 'sea_ice_speed' (float): Drift speed (m s⁻¹).
                    - 'sea_ice_speed_kmdy' (float): Drift speed (km day⁻¹).
                    - 'direction_of_sea_ice_displacement' (float): Forward
                                                                   azimuth
                                                                   (degrees).
                    - 'distance' (float): Euclidean displacement distance
                                          in projected space:
                                          sqrt(dx² + dy²) (m).
                    - 'distance_geod' (float): Geodesic distance on the
                                               WGS84 ellipsoid (m).
                Outlier flag (level-dependent):
                    - 'outlier_category' (str): Two-digit outlier code;
                      included when config['level'] in ['00', '02', '03'].
                      For level '03', only rows with values '00' or '01'
                      are retained and the value is recoded to -1 before
                      writing.
                Scene identifier:
                    - 'scene_id' (str): Used as part of the layer name for
                      levels '00' and '02'.
        gpkg_path (str): Full path for the output GeoPackage file.
        config (dict): Configuration dictionary containing:
                - 'epsg' (int): EPSG code of the projected CRS used for
                                `X1`, `Y1`, `X2`, `Y2` coordinates and set
                                as the GeoPackage layer CRS.
                - 'level' (str): Processing level; controls layer structure
                                 and outlier filtering:
                                     '00': one layer per scene, all vectors
                                     '02': one layer per scene, all vectors
                                           with outlier_category included
                                     '03': single layer, inliers only,
                                           outlier_category recoded to -1
                - 'outlier_qml_file' (str): Path to the QML style file used
                                            for level '02' (colors vectors
                                            by outlier category).
                - 'graduated_qml_file' (str): Path to the QML style file
                                              used for all other levels
                                              (colors vectors by displacement
                                              magnitude).

    Returns:
        None, or None early if level '03' and no inlier rows survive
        filtering.

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
        - For levels '00' and '02', layers are named
          `drift_vectors_<scene_id>`. The first scene is written with
          mode='w' and subsequent scenes with mode='a' to append layers
          without overwriting.
        - For level '03', duplicate starting positions (longitude_1,
          latitude_1) are dropped keeping the last occurrence, and a
          warning is logged if any duplicates are found.
        - The QML style is embedded via `_embed_qml_style` for each layer,
          so end users do not need the QML file present to load the styled
          layer in QGIS.
    """

    import os
    import numpy as np
    import logging
    import geopandas as gpd
    from shapely.geometry import LineString

    logger = logging.getLogger('sar_drift_converter')
    
    if config['overwrite'] and os.path.exists(gpkg_path):
        # make sure GeoPackage doesn't append to existing file
        os.remove(gpkg_path)
    
    df_local = df.copy()

    # keep necessary columns for GeoPackage
    needed_cols = [
        'scene_id', 'sensor1', 'sensor2',
        'longitude_1', 'latitude_1', 'longitude_2', 'latitude_2',
        'X1', 'Y1', 'X2', 'Y2',
        'date_start', 'date_end', 'duration',
        'sea_ice_x_displacement', 'sea_ice_y_displacement',
        'u', 'v','sea_ice_speed', 'sea_ice_speed_kmdy',
        'direction_of_sea_ice_displacement', 'distance', 'distance_geod',
        'outlier_category'
    ]        
    df_local=df_local[needed_cols]
    
    
    
    if config['level'] in ['00', '02']:
        # write one layer per scene
        unique_test = {}
        scene_idx = 0
        for scene_id, df_scene in df_local.groupby('scene_id'):
            df_scene = df_scene.copy()
            
            layer_name = _get_layer_name(scene_id)
    
            if layer_name not in unique_test:
                unique_test[layer_name] = ''
            else:
                df_scene.to_csv('duplicate_scene_ids', index=True)
                logger.warning(
                    'Duplicate scene id found. |'
                    f'Scene ID: {scene_id} Layer Name: {layer_name}'
                )
            
            df_scene['geometry_line'] = df_scene.apply(
                lambda row: LineString(
                    [(row['X1'], row['Y1']), (row['X2'], row['Y2'])]
                ),
                axis=1
            )
        
            gdf_line = gpd.GeoDataFrame(df_scene, geometry='geometry_line')
            gdf_line['geometry_type'] = 'line'
            gdf_line = gdf_line.rename(
                columns={'geometry_line': 'geometry'}
            ).set_geometry('geometry')
            gdf_line = gdf_line.set_crs(f'EPSG:{config["epsg"]}')
        
            # append mode adds layers if file exists
            write_mode = 'w' if scene_idx == 0 else 'a'
            gdf_line.to_file(
                gpkg_path, layer=layer_name, driver='GPKG', mode=write_mode
            )
            scene_idx += 1
        
            # embed QML style for this layer
            _embed_qml_style(gpkg_path, layer_name, config)
            
    else:
        # taking latest observation for duplicate cells
        
        # For level 03, retain only inlier vectors
        # (outlier_category 00 or 01), then recode to -1 to signal that
        # outlier filtering has been applied.
        outlier_filter = df_local['outlier_category'].isin(['00', '01'])
        df_local = df_local[outlier_filter].copy()
        df_local['outlier_category'] = -1
        if df_local.shape[0] == 0:
            # it might be possible the data frame was labelled
            # as all outliers.
            return None
    
        # two vectors can have slightly different lon/lat but map to
        # the same 12.5 km grid cell - keep last occurrence, consistent
        # with NetCDF and HTML/JSON output deduplication strategy
        lons = df_local['longitude_1'].to_numpy()
        lats = df_local['latitude_1'].to_numpy()
        lons_normalized = np.where(lons < 0, lons + 360, lons)
        i, j = _polar_lonlat_to_ij(
            lons_normalized,
            lats,
            grid_size=12.5,
            hemisphere='north'
        )
        df_local['_grid_i'] = i
        df_local['_grid_j'] = j
        dupes = df_local.duplicated(
            subset=['_grid_i', '_grid_j'], keep='last'
        )
        if dupes.any():
            logger.info(
                f"Level 03 GeoPackage: dropping {dupes.sum()} duplicate "
                "grid cell vector(s). Keeping last occurrence"
            )
        df_local = df_local[~dupes].drop(columns=['_grid_i', '_grid_j'])
    
        df_local['geometry_line'] = df_local.apply(
            lambda row: LineString(
                [
                    (row['X1'], row['Y1']),
                    (row['X2'], row['Y2'])
                ]
            ),
            axis=1
        )
    
        gdf_line = gpd.GeoDataFrame(df_local, geometry='geometry_line')
        gdf_line['geometry_type'] = 'line'
    
        gdf_line = gdf_line.rename(
            columns={'geometry_line': 'geometry'}
        ).set_geometry('geometry')
        gdf_line = gdf_line.set_crs(f'EPSG:{config["epsg"]}')
        gdf_line.to_file(gpkg_path, layer='drift_vectors', driver='GPKG')
    
        # embed .qml outlier layer style
        _embed_qml_style(gpkg_path, 'drift_vectors', config)
        
    # log activity
    logger.info(f'Created GeoPackage {gpkg_path}')
           
    
def create_vector_html_and_json(df, html_path, data_dir, si_json_path,
                                buoy_json_path, available_dates_path, config):
    """
    Serialize drift vector observations to a compact JSON file and write
    an accompanying interactive HTML viewer.

    Writes a single JSON object containing date metadata and a list of
    per-vector entries, then produces a self-contained HTML file that loads
    the JSON from the `data/` subdirectory and renders drift vectors on an
    interactive Leaflet polar stereographic map. For level '03', only inlier
    vectors are retained and their outlier category is recoded to '-1' before
    writing.

    Args:
        df (pandas.DataFrame): Input drift observations. Expected columns:
                - 'longitude_1', 'latitude_1' (float): Start position
                  (EPSG:4326, degrees).
                - 'longitude_2', 'latitude_2' (float): End position
                  (EPSG:4326, degrees).
                - 'duration' (float): Observation duration (s); written as
                  a rounded integer in each vector entry.
                - 'date_start' (datetime-like): Start timestamp; the minimum
                  value across all rows is written as `date1`
                  (format: 'YYYY-MM-DD').
                - 'date_end' (datetime-like): End timestamp; the maximum
                  value across all rows is written as `date2`
                  (format: 'YYYY-MM-DD').
                - 'outlier_category' (str): Two-digit outlier code. For level
                  '03', only rows with values '00' or '01' are retained and
                  the value is recoded to '-1' before writing.
        html_path (str): Full path for the output HTML viewer file. The
                         parent directory must already exist. The HTML file
                         references the JSON using only the basename of
                         `json_path` under a `data/` prefix, so the JSON
                         file must be placed in a `data/` subdirectory
                         relative to the HTML file's location.
        data_dir (str): Directory where reference GeoJSON template files
                        (land, coastline, graticule) are confirmed to exist
                        via `_add_json_templates`. Must be the `data/`
                        subdirectory served alongside the HTML file.
        json_path (str): Full path for the output JSON file. Parent directory
                         must already exist.
        config (dict): Configuration dictionary. Must include:
                - 'level' (str): Processing level; if '03', only inlier
                  vectors (`outlier_category` in ['00', '01']) are written
                  and their `outlier_category` is recoded to '-1'.

    Returns:
        tuple[str, str] or tuple[None, None]: A two-element tuple
            `(json_path, html_path)` with the paths of the files written,
            or `(None, None)` if level is '03' and no rows survive the
            inlier filter.

    Notes:
        - Each entry in the `vectors` list follows the format:
            `[lon1, lat1, lon2, lat2, speed_x100, outlier_category]`
            where `speed_x100` is drift speed in km/day multiplied by 100
            and rounded to the nearest integer.
        - `count` reflects the number of vectors actually written, after
          any level '03' filtering.
        - The JSON is written without indentation for compact output.
        - The HTML viewer is produced by reading the template at
          `config['html_template_file']` and replacing the hardcoded JSON
          filename in the `fetch('data/...')` call with the basename of
          `json_path`. All other HTML content is written unchanged.
        - The HTML viewer requires a `data/` subdirectory adjacent to the
          HTML file containing the JSON output and the reference GeoJSON
          files (land, coastline, graticule) confirmed by
          `_add_json_templates`.
    """

    import os
    import shutil
    import numpy as np
    import json
    import logging

    logger = logging.getLogger('sar_drift_converter')

    # confirm template GeoJSON reference files are in data_dir
    _add_json_templates(data_dir, config)
    
    # always update HTML viewer
    shutil.copy(config['html_vector_template'], html_path)


    df_local = df.copy()
    
    # For HTML output, retain only inlier vectors (outlier_category 00 or 01),
    outlier_filter = df_local['outlier_category'].isin(['00', '01'])
    df_local = df_local[outlier_filter].copy()

    if df_local.shape[0] == 0:
        # it might be possible the data frame was labelled as all outliers
        # unlikely, but it needs to be handled
        return
    
    
    # sort by end date so the duplicate gaurantees to take the last index
    # that has the latest time stamp
    df_local = df_local.sort_values('date_end', ascending=True)
    
    # two vectors can have slightly different lon/lat but map to
    # the same 12.5 km grid cell. if so, keep the latest (i, j) grid cell
    lons = df_local['longitude_1'].to_numpy()
    lats = df_local['latitude_1'].to_numpy()
    lons_normalized = np.where(lons < 0, lons + 360, lons)
    i, j = _polar_lonlat_to_ij(
        lons_normalized,
        lats,
        grid_size=12.5,
        hemisphere='north'
    )
    df_local['_grid_i'] = i
    df_local['_grid_j'] = j

    dupes = df_local.duplicated(
        subset=['_grid_i', '_grid_j'],
        keep='last'
    )
    if dupes.any():
        df_local = df_local[~dupes]
        logger.warning(
            f'Level 03 HTML: dropping {dupes.sum()} duplicate '
             'starting lon/lat vector(s). Keeping last occurrence of '
            f'{df_local.shape[0]} vector(s).'
        )
        
    date1 = df_local['date_start'].min().strftime('%Y-%m-%d')
    date2 = df_local['date_end'].max().strftime('%Y-%m-%d')
    
    
    vectors = [
        [
            float(row.longitude_1),
            float(row.latitude_1),
            float(row.longitude_2),
            float(row.latitude_2),
            float(row.sea_ice_speed_kmdy),
            float(row.direction_of_sea_ice_displacement)
        ]
        for row in df_local.itertuples(index=False)
    ]

    payload = {
        'date1': date1,
        'date2': date2,
        'count': len(vectors),
        'vectors': vectors
    }

    with open(si_json_path, 'w', encoding='utf-8') as f:
        json.dump(payload, f, separators=(',', ':'))                

    logger.info(f'Created JSON {si_json_path}')
    
    
    # Add buoy_json
    df_buoy_drift = config['buoy_drift']
    date_filter = (df_buoy_drift['date'].astype(str) == date1)
    buoy_daily_drift = df_buoy_drift[date_filter].reset_index(drop=True).copy()
    
    vectors = [
        [
            float(row.longitude_1),
            float(row.latitude_1),
            float(row.longitude_2),
            float(row.latitude_2),
            float(row.speed_kmdy),
            float(row.bearing)
        ]
        for row in buoy_daily_drift.itertuples(index=False)
    ]

    payload = {
        'date1': date1,
        'date2': date2,
        'count': len(vectors),
        'vectors': vectors
    }
    
    if len(vectors) > 0:
        # only create bouy JSON if there are buoy data.
        # Data avaliable lags to SAR drift data available.
        with open(buoy_json_path, 'w', encoding='utf-8') as f:
            json.dump(payload, f, separators=(',', ':'))                
    
        logger.info(f'Created JSON {buoy_json_path}')
    
    
    # update available dates
    if os.path.exists(available_dates_path):
        with open(available_dates_path, 'r', encoding='utf-8') as f:
            available_dates = set(json.load(f))
    else:
        available_dates = set()
    
    if date1 not in available_dates:
        available_dates.add(date1.replace('-', ''))
        with open(available_dates_path, 'w', encoding='utf-8') as f:
            json.dump(sorted(available_dates), f, separators=(',', ':'))
# -*- coding: utf-8 -*-
"""
******************************************************************************

 Project:     SAR Drift Converter
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
# Grid projections
#
# Polar stereographic
# Grid navigation functions from 
# https://github.com/nsidc/polarstereo-lonlat-convert-py/blob/
# main/polar_convert/polar_convert.py
#
# EASE 2.0 Grid
# https://nsidc.org/data/user-resources/help-center/guide-ease-grids
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

    
def _ease2_lonlat_to_ij(lons, lats, config):
    """
    Convert WGS84 lon/lat to EASE-Grid 2.0 North 12.5 km grid indices.

    Projects geographic coordinates (EPSG:4326) into EASE-Grid 2.0 North
    (EPSG:6931) and computes 0-based (i, j) grid cell indices, where i is
    the column (x direction) and j is the row (y direction, 0 = top/north).

    Expects standard -180 to 180 longitudes (unlike _polar_lonlat_to_ij
    which requires 0-360).

    Parameters:
        lons (array-like): Longitudes in degrees (-180 to 180, EPSG:4326).
        lats (array-like): Latitudes in degrees (EPSG:4326).
        config (dict): Configuration dictionary. Must include:
            - 'transformer_6931' (pyproj.Transformer): Cached transformer
              for EPSG:4326 → EPSG:6931 conversion. Created once upstream
              and reused across calls to avoid the per-call cost of
              Transformer.from_crs(), which involves PROJ database access
              and pipeline compilation.

    Returns:
        tuple: (i, j) as numpy int64 arrays of grid column and row indices.
               Points outside the grid are not explicitly checked; callers
               should validate against grid bounds if needed.
    """
    
    import numpy as np

    EASE2_N_ORIGIN_X = -9_000_000.0
    EASE2_N_ORIGIN_Y =  9_000_000.0
    RES = 12_500.0


    mx, my = config['transformer_6931'].transform(lons, lats)

    i = np.floor((mx - EASE2_N_ORIGIN_X) / RES).astype(np.int64)
    j = np.floor((EASE2_N_ORIGIN_Y - my) / RES).astype(np.int64)

    return i, j  


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
    configured web directory, limited to the reprocess window.

    Scrapes the HTML directory listing at the URL specified in
    `config['sar_drift_data_url']`, filters for matching gfilter
    filenames dated within `config['reprocess_days']` of today, and
    downloads them into the local download directory.

    Args:
        config (dict): Configuration dictionary. Must include:
                - 'sar_drift_data_url' (str): URL of the directory
                  listing page hosting SAR drift gfilter text files.
                - 'sar_drift_download_directory' (str): Local directory
                  path where downloaded files are saved.
                - 'reprocess_days' (int): Number of days back from today
                  to download. Files whose embedded date is older than
                  this window are skipped.

    Workflow:
        1. Send a GET request to `config['sar_drift_data_url']` and
           parse the HTML directory listing using BeautifulSoup.
        2. Filter all `<a>` href links for filenames matching the
           gfilter pattern `SARIceDrift_EG125_*T0000_*T2359_gfilter1.txt`.
        3. Skip links beginning with `?` or `/` (navigation and
           parent directory entries).
        4. Parse the YYYYDDD (year + day-of-year) date token from each
           matched filename and keep only files dated on or after
           (today - reprocess_days).
        5. Download each remaining file, logging each download.
        6. Log and return early if no matching files are found.

    Returns:
        None

    Raises:
        requests.HTTPError: If the directory listing request returns a
            non-2xx status code, via `raise_for_status()`.
        requests.RequestException: If a network error occurs during the
            directory listing request. Individual file download errors
            are caught and logged rather than raised.

    Notes:
        - SSL verification is disabled for all requests via
          `verify=False`. InsecureRequestWarning is suppressed via
          `urllib3.disable_warnings()`.
        - The date window mirrors the `reprocess_days` logic in
          `_check_existing_files`, so the set of days downloaded matches
          the set of days whose output is force-regenerated.
        - The download directory is expected to have been cleared by
          `_clear_download_dir` before this function runs, so files are
          re-downloaded fresh each run within the window.
        - `base_url` is normalized to end with `/` before constructing
          absolute download links via `urljoin`, preventing the final
          path component from being dropped.
        - A per-filename date-parse failure logs a warning and skips that
          file rather than aborting the run.
        - Download progress is displayed via a `tqdm` progress bar.
    """

    import logging
    from tqdm import tqdm
    import os
    import pandas as pd
    import requests
    from bs4 import BeautifulSoup
    from urllib.parse import urljoin
    import urllib3
    import ssl
    from requests.adapters import HTTPAdapter
    from urllib3.util.ssl_ import create_urllib3_context
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


    # cutoff date for how far back to download, based on reprocess_days
    reprocess_days = config['reprocess_days']
    cutoff = (
        pd.Timestamp.now().normalize() - pd.Timedelta(days=reprocess_days)
    )

    # Filter for Arctic-wide gfilter.txt files within the reprocess window
    download_links = []
    for link in links:
        if link.startswith('SARIceDrift_EG125_') and \
           link.endswith('T2359_gfilter1.txt') and \
           'T0000_' in link:
            # date token is YYYYDDD (year + day-of-year) after the prefix,
            # e.g. 'SARIceDrift_EG125_2025350T0000_...' -> '2025350'
            date_token = link.split('_')[2][:7]
            try:
                file_date = pd.to_datetime(date_token, format='%Y%j')
            except ValueError:
                logger.warning(
                    f"Could not parse date from {link}; skipping"
                )
                continue
            if file_date >= cutoff:
                download_links.append(urljoin(base_url, link))


    # Download each file
    if len(download_links) == 0:
        logger.info("No new gfilter files found to download")
        return

    download_folder = config['sar_drift_download_directory']
    tqdm_desc = "Downloading SAR drift gfilter files"


    class TLSAdapter(HTTPAdapter):
        """
        Custom HTTP adapter that overrides the default SSL context to handle
        TLS negotiation issues with www.star.nesdis.noaa.gov. The server
        intermittently closes connections during handshake with default
        urllib3 TLS settings. Using a permissive cipher suite and disabling
        cert verification resolves the EOF errors seen with standard requests.
        """
        def init_poolmanager(self, *args, **kwargs):
            ctx = create_urllib3_context()
            ctx.set_ciphers('DEFAULT')
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            kwargs['ssl_context'] = ctx
            return super().init_poolmanager(*args, **kwargs)

    with requests.Session() as session:
        session.mount('https://', TLSAdapter())

        for file_url in tqdm(
                download_links, desc=tqdm_desc, unit=' file', colour='green'):
            filename = os.path.basename(file_url)
            local_path = os.path.join(download_folder, filename)
            try:
                r = session.get(file_url, verify=False, timeout=(10, 120))
                r.raise_for_status()
                with open(local_path, 'w') as f:
                    f.write(r.text)
                logger.info(f"Downloaded {filename}")
            except requests.exceptions.RequestException as e:
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
    Determine which expected daily output files already exist for a given day.

    Returns a dictionary mapping each output type to a bool indicating
    whether that file already exists on disk, allowing the processing loop
    to skip only the outputs already present rather than the entire day.
    Days within the `reprocess_days` window (or any run with `overwrite`
    True) are forced to regenerate by returning all-False flags for the
    output types the level produces.

    Args:
        scene_output_stub (dict): Lightweight dict of date bounds for the
            day being checked. Must contain:
                - `start_date` (pandas.Timestamp): Minimum date_start for
                  the day.
                - `end_date`   (pandas.Timestamp): Maximum date_end for
                  the day.
        config (dict): Configuration dictionary. Must include:
                - `file_server_3413` / `file_server_6931` (str): Root output
                  path for the active EPSG.
                - `viewer_dir` (str): Viewer subdirectory under the file
                  server (used to locate existing vector JSON).
                - `epsg` (int): Active projected CRS code.
                - `level` (str): Processing level ('00'–'03').
                - `version` (str): Version string for filename construction.
                - `overwrite` (bool): If True, force regeneration of all
                  outputs the level produces.
                - `reprocess_days` (int): Days back from today within which
                  outputs are always regenerated.

    Returns:
        dict: Keys `nc_scenes`, `nc_daily`, `gpkg`, `json`; values are bool
            indicating whether the file exists (True) or needs writing
            (False). Output types a level does not produce are reported as
            True (treated as already satisfied) so callers can use
            `all(exists.values())` to decide whether to skip a day entirely.

    Notes:
        - If `start_date` falls within `reprocess_days` of today, or
          `overwrite` is True, the function returns immediately with the
          per-level force-regenerate flag set (False for produced outputs,
          True for unproduced ones).
        - Checked paths mirror exactly the paths written by
          `create_daily_output`:
            - NetCDF (scenes/daily) and GeoPackage under
              `<file_server_<epsg>>/<data_files_dir>/PL<level>/
              <year>/{nc,gpkg}/`.
            - Vector JSON under
              `<file_server_<epsg>>/<viewer_dir>/SIVelocity_SAR/
              si_velocity_<start>.json`.
        - Output coverage by level: scenes NetCDF for '00'/'01'/'02';
          daily NetCDF for all levels; GeoPackage for '00'/'02'/'03';
          vector JSON for '00'/'03'.
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
            f'Recreating output since {start_date} is within reprocess window '
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
    lvl   = f"PL{config['level']}"
    yr    = start[:4]
    file_server = config[f"file_server_{epsg}"]
    nc_dir   = os.path.join(file_server, lvl, yr, 'nc')
    gpkg_dir = os.path.join(file_server,  lvl, yr, 'gpkg')


    # check NetCDF scenes
    nc_scenes_exists = True
    if config['level'] in ['00', '01', '02']:
        nc_scenes_exists = os.path.exists(os.path.join(
            nc_dir,
            f"SIVelocity_SAR_{start}_{end}_scenes_12km_NH_{epsg}"
            f"_PL{config['level']}_v{config['version']}.nc"
        ))
        
    # check NetCDF daily
    nc_daily_exists = True
    if config['level'] in ['00', '01', '02', '03']:
        nc_daily_exists = os.path.exists(os.path.join(
            nc_dir,
            f"SIVelocity_SAR_{start}_{end}_daily_12km_NH_{epsg}"
            f"_PL{config['level']}_v{config['version']}.nc"
        ))

    # check GeoPackage
    gpkg_exists = True
    if config['level'] in ['00', '02', '03']:
        gpkg_exists = os.path.exists(os.path.join(
            gpkg_dir,
            f"SIVelocity_SAR_{start}_{end}_daily_12km_NH_{epsg}"
            f"_PL{config['level']}_v{config['version']}.gpkg"
        ))
        
    # check JSON
    json_exists = True
    if config['level'] in ['00', '03']:
        json_exists = os.path.exists(
            os.path.join(
                config['json_dir'],
                f"SIVelocity_SAR_{start}_{end}_daily_12km_NH_{epsg}"
                f"_PL{config['level']}_v{config['version']}.json"
            )
        )

   
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
    
    
def _load_cdl_as_dataset(config):
    """
    Generate an in-memory xarray Dataset from an EPSG-specific CDL file.

    Constructs the EPSG-specific CDL filename from the base CDL path in
    config (e.g. 'sar_drift_output.cdl' becomes
    'sar_drift_output_3413.cdl'), runs `ncgen` to convert it to a temporary
    NetCDF file in a 'tmp' subdirectory of meta_dir, loads the result into
    memory, then deletes the temporary file. No .nc file is permanently
    written to the meta directory.

    The returned dataset contains only metadata (attributes and structure)
    and is used as a template whose attributes and coordinates are applied
    to a data-driven NetCDF file.

    Parameters:
        config (dict): Configuration dictionary containing:
            - 'meta_dir' (str): Directory containing CDL files. A 'tmp'
                                subdirectory is created here if it does
                                not already exist.
            - 'netcdf_cdl_file' (str): Base CDL filename
                                       (e.g. 'sar_drift_output.cdl').
            - 'epsg' (str | int): EPSG code used to select the correct
                                  CDL file (e.g. 3413 or 6931).

    Returns:
        xarray.Dataset: In-memory dataset containing metadata, coordinates,
                        and empty data variables from the CDL template,
                        opened with decode_times=False.

    Raises:
        SystemExit: If the CDL file is not found or `ncgen` returns a
                    non-zero exit code.
    """
    
    import util
    import os
    import subprocess
    import xarray as xr

    cdl_file_path = config[f"netcdf_cdl_file_{config['epsg']}"]
    cdl_file_basename = os.path.splitext(os.path.basename(cdl_file_path))[0]

    if not os.path.exists(cdl_file_path):
        util.error_msg(f"Cannot find `{cdl_file_path}`")

    tmp_dir = os.path.join(config['meta_dir'], 'tmp')
    os.makedirs(tmp_dir, exist_ok=True)
    tmp_nc = os.path.join(tmp_dir, f'{cdl_file_basename}.nc')

    try:
        rc = subprocess.call(
            f'ncgen -o {tmp_nc} {cdl_file_path}',
            shell=True
        )
        if rc != 0:
            util.error_msg(
                'Error in `ncgen` call. Cannot continue.\n'
                f'Command: ncgen -o {tmp_nc} {cdl_file_path}\n'
                f'Error Code: {rc}'
            )
        with xr.open_dataset(tmp_nc, decode_times=False) as ds:
            return ds.load()
    finally:
        if os.path.exists(tmp_nc):
            os.remove(tmp_nc)


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


def _set_linux_permissions(path, mode=0o664):
    """
    Set file permissions on an output file after writing.

    On Linux/Mac, applies the specified octal mode (defaults to 0o664,
    rw-rw-r--, per web server policy). On Windows, this call is skipped
    since Unix permission bits are not supported.

    Args:
        path (str): Path to the file.
        mode (int): Octal permission mode. Defaults to 0o664.
    """
    import os
    import platform
    if platform.system() != 'Windows' and os.path.exists(path):
        try:
            os.chmod(path, mode)
        except PermissionError:
            # safely pass directories where there is no permission allowed
            pass
        
        
def _clear_download_dir(config):
    """
    Remove all downloaded gfilter files from the local download directory.

    Called at the end of each pipeline run to reclaim disk space after
    output has been written.

    Args:
        config (dict): Configuration dictionary. Required keys:
            - 'sar_drift_download_directory' (str): Directory containing
            downloaded gfilter files.

    Returns:
        int: Number of files deleted.

    Side Effects:
        - Deletes downaloded files from config['sar_drift_download_directory'].
        - Logs the count of files deleted at INFO level.
    """
    
    import os
    import logging

    logger  = logging.getLogger('ascat_ice_classification_converter')
    deleted = 0

    for filename in os.listdir(config['sar_drift_download_directory']):
        file_path = os.path.join(
            config['sar_drift_download_directory'], filename
        )
        os.remove(file_path)
        deleted += 1

    logger.info(
        f'Cleared {deleted} NetCDF files from '
        f'{config["sar_drift_download_directory"]}'
    )
    return deleted        
        
        
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
            unit=' file',
            file=sys.stdout,
            dynamic_ncols=True,
            colour='green', miniters=1000, mininterval=0
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
                unit=' scene',
                colour='green'
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
                config['test_output_dir'], 'filtered_combined.csv'
            ),
            index=False
        )    
    
    return df_all


###############
# Create Output
###############

def create_netcdf(df, nc_path, config, template_ds, multi_layered=False):
    """
    Create a gridded NetCDF sea-ice drift product from point/vector
    observations. Supports both single-scene and multi-scene (daily)
    output in one unified function.

    Maps input drift vectors onto the target projection grid using the
    EPSG code in config, populates a NetCDF dataset using attributes from
    a pre-built template dataset, and writes the result to disk with
    compression. The output grid is allocated pre-cropped to the spatial
    extent of all observations (with padding) so the full NSIDC grid is
    never held in memory.

    For single-scene output (`multi_layered=False`), the DataFrame is
    treated as one scene and written as a single time layer. For daily
    output (`multi_layered=True`), the DataFrame is grouped by `scene_id`
    and each group is written as a separate time layer on the shared grid.
    In both cases the output is cropped to the bounding box of all
    observations across the full DataFrame.

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
                  retained and recoded to np.int16(-1) before writing.
                - 'Maxcorr1', 'Maxcorr2' (float): Cross-correlation
                  scores; used for `measurement_error` flag in levels
                  '00'/'01'.
                - '_use_75km' (bool): Whether the 75 km file was used;
                  controls speed threshold for `speed_error` flag. For
                  multi-layered output this is evaluated per scene group
                  since different scenes may differ.
        nc_path (str): Full output path for the NetCDF file.
        config (dict): Configuration dictionary. Must include:
                - 'level' (str): Processing level ('00'–'03'); controls
                  inlier filtering, error flag computation, and fill
                  value assignment.
                - 'epsg' (int): EPSG code controlling which grid index
                  function is used. Supported values: 3413
                  (_polar_lonlat_to_ij) and 6931 (_ease2_lonlat_to_ij).
        template_ds (xarray.Dataset): Pre-built template dataset
            providing grid coordinate arrays, variable attributes, and
            global attributes. Built externally via
            `_load_cdl_as_dataset` and passed in to avoid redundant I/O
            across calls.
        multi_layered (bool): If False (default), writes a single time
            layer for the scene. If True, groups `df` by `scene_id` and
            writes one time layer per group for daily output.

    Returns:
        None

    Notes:
        - Grid indices are computed per EPSG: EPSG:3413 uses
          `_polar_lonlat_to_ij` with 0-360 normalized longitudes;
          EPSG:6931 uses `_ease2_lonlat_to_ij` with standard -180-180
          longitudes. An unsupported EPSG raises ValueError.
        - The grid is allocated pre-cropped: the (i, j) bounding box of
          all observations is computed up front with a 4-cell pad, the
          grid is allocated only at that size, and grid indices are
          shifted into the cropped frame before the populate loop. This
          avoids allocating the full NSIDC grid per time layer.
        - `time` coordinate uses minimum `date_start` per layer in
          seconds since 2000-01-01.
        - `time_bnds` spans [min(date_start), max(date_end)] per time
          layer.
        - `layer_id` is set to the formatted scene_id for each time
          layer.
        - If two observations map to the same (i, j) within a time layer,
          the last one written wins (numpy fancy-index behavior).
        - All int16 flag variables use -9 as `_FillValue`.
        - For level '03', `outlier_category` is recoded to np.int16(-1)
          for all retained observations.
        - For level '03', if no rows survive the inlier filter the
          function returns early with no file written.
        - For `multi_layered=True`, `speed_error` threshold is evaluated
          per scene group using that group's `_use_75km` value, since
          scenes within a day may differ.
        - `bearing_error` is set to 1 if `direction_of_sea_ice_
          displacement == 0` and `sea_ice_speed <= 0`, else 0.
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
        df_copy['outlier_category'] = np.int16(-1)
        if df_copy.shape[0] == 0:
            logger.info('All outliers found. No data to process.')
            return

    # compute error flags per row for levels 00/01
    if config['level'] in ['00', '01']:
        df_copy['bearing_error'] = (
            (df_copy['direction_of_sea_ice_displacement'] == 0) &
            (df_copy['sea_ice_speed'] <= 0)
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

    if config['epsg'] == 3413:
        # _polar_lonlat_to_ij expects 0-360 longitudes
        lons_normalized = np.where(lons < 0, lons + 360, lons)
        i_all, j_all = _polar_lonlat_to_ij(
            lons_normalized, lats, grid_size=12.5, hemisphere="north"
        )

        # xmin/ymin from _grid_params are already cell centers (km),
        # converted to metres here. y flipped to top-down (row 0 = north)
        # to match the j-flip inside _polar_lonlat_to_ij.
        RES = 12_500.0
        _, imax, jmax, xmin, ymin = _grid_params(12.5, NORTH)
        x_coords = (xmin * 1000) + RES * np.arange(imax)
        y_coords = (ymin * 1000) + RES * np.arange(jmax)
        y_coords = y_coords[::-1]  # flip y-coordinates

    elif config['epsg'] == 6931:
        i_all, j_all = _ease2_lonlat_to_ij(lons, lats, config)

        # Cell centers computed from EASE-Grid 2.0 North origin constants.
        RES = 12_500.0
        x_coords = -9_000_000.0 + RES * np.arange(1440) + RES / 2
        y_coords =  9_000_000.0 - RES * np.arange(1440) - RES / 2


    # assign EPSG-specfic i,j values to data frame copy
    i_all = np.asarray(i_all, dtype=np.int64)
    j_all = np.asarray(j_all, dtype=np.int64)
    df_copy = df_copy.reset_index(drop=True)
    df_copy['grid_i'] = i_all
    df_copy['grid_j'] = j_all


    # determine the bounding box across all observations up front so the
    # grid is allocated at cropped size rather than the full NSIDC extent.
    # this is the key memory reduction: a day whose scenes touch only a
    # small region no longer allocates the entire polar grid per layer.
    pad_cells = 4
    full_y = template_ds.sizes['y']
    full_x = template_ds.sizes['x']
    y_start = max(0, int(j_all.min()) - pad_cells)
    y_end   = min(full_y - 1, int(j_all.max()) + pad_cells)
    x_start = max(0, int(i_all.min()) - pad_cells)
    x_end   = min(full_x - 1, int(i_all.max()) + pad_cells)

    # shift indices into the cropped frame
    df_copy['grid_i'] = df_copy['grid_i'] - x_start
    df_copy['grid_j'] = df_copy['grid_j'] - y_start

    # slice coordinate arrays to the cropped extent
    x_coords = x_coords[x_start:x_end + 1]
    y_coords = y_coords[y_start:y_end + 1]


    # determine scene groups and time layer count
    epoch = pd.Timestamp('2000-01-01')

    if multi_layered:
        scene_groups = [
            (sid, grp.reset_index(drop=True))
            for sid, grp in df_copy.groupby('scene_id', sort=True)
        ]
    else:
        scene_groups = [(df_copy['scene_id'].iloc[0], df_copy)]

    n_time = len(scene_groups)

    grid_shape = (
        n_time,
        y_end - y_start + 1,
        x_end - x_start + 1
    )

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
        global_attrs = template_ds.attrs.copy()
        sea_ice_speed_attrs = template_ds["sea_ice_speed"].attrs.copy()
        sea_ice_x_attrs = template_ds["sea_ice_x_displacement"].attrs.copy()
        sea_ice_y_attrs = template_ds["sea_ice_y_displacement"].attrs.copy()
        direction_attrs = (
            template_ds["direction_of_sea_ice_displacement"].attrs.copy()
        )
        outlier_attrs = template_ds["outlier_category"].attrs.copy()
        bearing_error_attrs = template_ds["bearing_error"].attrs.copy()
        speed_error_attrs = template_ds["speed_error"].attrs.copy()
        measurement_error_attrs = template_ds["measurement_error"].attrs.copy()
        spatial_ref_attrs = template_ds["spatial_ref"].attrs.copy()
        x_attrs = template_ds["x"].attrs.copy()
        y_attrs = template_ds["y"].attrs.copy()
        time_attrs = template_ds["time"].attrs.copy()
        layer_id_attrs = template_ds["layer_id"].attrs.copy()
        time_attrs['coordinates'] = 'layer_id'

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
            ix = grp['grid_i'].to_numpy(dtype=np.int64)
            iy = grp['grid_j'].to_numpy(dtype=np.int64)

            g = netcdf_grid  # alias to keep lines short
            g["sea_ice_speed"].values[t_idx, iy, ix] = (
                grp['sea_ice_speed'].to_numpy(dtype=np.float32))
            g["sea_ice_x_displacement"].values[t_idx, iy, ix] = (
                grp['sea_ice_x_displacement'].to_numpy(dtype=np.float32))
            g["sea_ice_y_displacement"].values[t_idx, iy, ix] = (
                grp['sea_ice_y_displacement'].to_numpy(dtype=np.float32))
            g["direction_of_sea_ice_displacement"].values[t_idx, iy, ix] = (
                grp['direction_of_sea_ice_displacement']
                .to_numpy(dtype=np.float32))
            g["outlier_category"].values[t_idx, iy, ix] = (
                grp['outlier_category'].to_numpy(dtype=np.int16))
            g["bearing_error"].values[t_idx, iy, ix] = (
                grp['bearing_error'].to_numpy(dtype=np.int16))
            g["speed_error"].values[t_idx, iy, ix] = (
                grp['speed_error'].to_numpy(dtype=np.int16))
            g["measurement_error"].values[t_idx, iy, ix] = (
                grp['measurement_error'].to_numpy(dtype=np.int16))


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

        # set Linux/Mac permissions on file
        _set_linux_permissions(nc_path)

        logger.info(f'Created NetCDF {nc_path}')

    finally:
        if netcdf_grid is not None:
            netcdf_grid.close()
            del netcdf_grid


def create_shape_package(df, gpkg_path, config):
    """
    Create a GeoPackage containing drift line vectors for SAR drift data.

    Snaps all observations to the nearest grid cell center for the
    configured projection (EPSG:3413 or EPSG:6931) before building
    geometries, consistent with the NetCDF output. LineString geometries
    are built from the snapped start position to the snapped start plus
    displacement (X1_snapped + dx, Y1_snapped + dy). For levels '00' and
    '02', one layer is written per scene pair, named
    `drift_vectors_<scene_id>`. For level '03', a single `drift_vectors`
    layer is written containing only inlier vectors (outlier_category '00'
    or '01'), with outlier_category recoded to -1 and duplicate grid cells
    deduplicated keeping the last occurrence. A QML style file is embedded
    directly into the GeoPackage's `layer_styles` table for each layer for
    automatic styling when opened in QGIS.

    Args:
        df (pandas.DataFrame): Input DataFrame containing drift vectors, as
            produced by `read_sar_drift_data_file` and `outlier_search`.
            Expected columns:
                Projected coordinates (EPSG:`config['epsg']`, metres):
                    - 'X1', 'Y1' (float): Start position (overwritten by
                      snapped grid cell center before writing).
                    - 'X2', 'Y2' (float): End position (overwritten by
                      snapped start plus displacement before writing).
                Geographic coordinates (degrees):
                    - 'longitude_1', 'latitude_1' (float): Start lon/lat;
                      used to compute grid cell snap position.
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
                    - 'sea_ice_x_displacement' (float): X displacement (m);
                      added to snapped X1 to compute X2.
                    - 'sea_ice_y_displacement' (float): Y displacement (m);
                      added to snapped Y1 to compute Y2.
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
                - 'epsg' (int): EPSG code controlling both the grid snap
                                function and the GeoPackage layer CRS.
                                Supported values: 3413
                                (_polar_lonlat_to_ij, _grid_params) and
                                6931 (_ease2_lonlat_to_ij).
                - 'level' (str): Processing level; controls layer structure
                                 and outlier filtering:
                                     '00': one layer per scene, all vectors
                                     '02': one layer per scene, all vectors
                                           with outlier_category included
                                     '03': single layer, inliers only,
                                           outlier_category recoded to -1
                - 'overwrite' (bool): If True and the output file exists,
                                      it is deleted before writing to
                                      prevent layer accumulation.
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
        - X1/Y1 are overwritten with the snapped grid cell center in the
          target projection. X2/Y2 are set to X1_snapped +
          sea_ice_x_displacement and Y1_snapped + sea_ice_y_displacement,
          consistent with NetCDF grid cell assignment.
        - For EPSG:3413, grid cell centers are derived from _grid_params()
          with 0-360 normalized longitudes passed to _polar_lonlat_to_ij().
          For EPSG:6931, cell centers use the EASE-Grid 2.0 North origin
          constants via _ease2_lonlat_to_ij().
        - Geometry is a LineString from snapped (X1, Y1) to snapped
          (X2, Y2) in EPSG:`config['epsg']` projected metres.
        - CRS is set to EPSG:`config['epsg']`.
        - A helper column `geometry_type` is added with the literal value
          `'line'` to identify the layer geometry type.
        - Only the columns listed in `needed_cols` are written; `_grid_i`
          and `_grid_j` are internal and excluded from all output layers.
        - For levels '00' and '02', layers are named
          `drift_vectors_<scene_id>`. The first scene is written with
          mode='w' and subsequent scenes with mode='a' to append layers
          without overwriting.
        - For level '03', duplicate grid cell assignments are dropped
          keeping the last occurrence, consistent with NetCDF deduplication
          behavior. A warning is logged if any duplicates are found.
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
    
    # snap all observations to grid cell centers, consistent with NetCDF
    lons = df_local['longitude_1'].to_numpy()
    lats = df_local['latitude_1'].to_numpy()
    
    if config['epsg'] == 3413:
        lons_normalized = np.where(lons < 0, lons + 360, lons)
        i, j = _polar_lonlat_to_ij(
            lons_normalized, lats, grid_size=12.5, hemisphere='north'
        )
        RES = 12_500.0
        _, imax, jmax, xmin, ymin = _grid_params(12.5, NORTH)
        x_snapped = (xmin * 1000) + RES * i
        y_snapped = (ymin * 1000) + RES * (jmax - 1 - j)
    elif config['epsg'] == 6931:
        i, j = _ease2_lonlat_to_ij(lons, lats, config)
        RES = 12_500.0
        x_snapped = -9_000_000.0 + RES * i + RES / 2
        y_snapped =  9_000_000.0 - RES * j - RES / 2
    
    df_local['_grid_i'] = i
    df_local['_grid_j'] = j
    df_local['X1'] = x_snapped
    df_local['Y1'] = y_snapped
    df_local['X2'] = x_snapped + df_local['sea_ice_x_displacement']
    df_local['Y2'] = y_snapped + df_local['sea_ice_y_displacement']
    
    
    
    if config['level'] in ['00', '02']:
        # write one layer per scene
        unique_test = {}
        scene_idx = 0
        for scene_id, df_scene in df_local.groupby('scene_id'):
            df_scene = df_scene.copy().drop(columns=['_grid_i', '_grid_j'])
            
            layer_name = _get_layer_name(scene_id)
    
            if layer_name not in unique_test:
                unique_test[layer_name] = ''
            else:
                if config['level'] == '00':
                    df_scene.to_csv(
                        os.path.join(
                            config['test_output_dir'],
                            'duplicate_scene_ids'
                        ),
                        index=True
                    )
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
            return None

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
        
     
    # set Linux/Mac permissions on file    
    _set_linux_permissions(gpkg_path)
    
    # log activity
    logger.info(f'Created GeoPackage {gpkg_path}')
           
    
def create_vector_json(df, json_path, available_dates_path, config):
    """
    Serialize grid-snapped inlier drift vectors to a compact JSON file for
    the static web viewer.

    Retains only inlier vectors (`outlier_category` '00' or '01'), snaps
    each observation's start position to the nearest grid cell center for
    the configured projection, adds the projected displacement to obtain the
    snapped endpoint, and back-projects both to EPSG:4326. Writes a single
    JSON object containing date metadata and a list of per-vector entries,
    and updates an `available_dates.json` index.

    Args:
        df (pandas.DataFrame): Input SAR drift observations. Expected
            columns:
                - 'longitude_1', 'latitude_1' (float): Start position
                  (EPSG:4326, degrees); used to compute the grid-cell snap
                  and overwritten with the back-projected snapped cell
                  center before writing.
                - 'longitude_2', 'latitude_2' (float): End position
                  (EPSG:4326, degrees); overwritten with the back-projected
                  snapped origin plus displacement before writing.
                - 'sea_ice_x_displacement', 'sea_ice_y_displacement' (float):
                  Projected displacement components (m); added to the snapped
                  origin to compute the snapped endpoint.
                - 'sea_ice_speed_kmdy' (float): Drift speed (km day⁻¹);
                  written directly to each vector entry.
                - 'direction_of_sea_ice_displacement' (float): Forward
                  azimuth (degrees); written directly to each vector entry.
                - 'date_start' (datetime-like): Start timestamp; minimum
                  across retained rows is written as `date1`.
                - 'date_end' (datetime-like): End timestamp; used for
                  duplicate resolution (latest kept) and maximum across
                  retained rows is written as `date2`.
                - 'outlier_category' (str): Two-digit outlier code; only
                  rows with '00' or '01' are retained.
        json_path (str): Full path for the output vector JSON file. Parent
                         directory must already exist.
        available_dates_path (str): Full path to the JSON index tracking all
                                     processed dates. Created if absent;
                                     `date1` is appended (in `YYYYMMDD` form)
                                     if not already present.
        config (dict): Configuration dictionary. Must include:
                - 'epsg' (int): EPSG code controlling the grid-snap
                                function. Supported: 3413
                                (`_polar_lonlat_to_ij`, `_grid_params`) and
                                6931 (`_ease2_lonlat_to_ij`).

    Returns:
        None. Returns early without writing if no rows survive the inlier
        filter.

    Notes:
        - The lon1/lat1 and lon2/lat2 written to the JSON are the
          back-projected EPSG:4326 positions of the snapped grid cell center
          and snapped endpoint, not the raw observation coordinates. This
          keeps the JSON consistent with the NetCDF and GeoPackage outputs.
        - Each entry in the `vectors` list has the format:
          `[lon1, lat1, lon2, lat2, speed_kmdy, bearing]`.
        - Rows are sorted by `date_end` ascending before deduplication so the
          latest observation wins when two vectors map to the same grid cell.
        - `_grid_i` and `_grid_j` are internal columns used only for
          deduplication and are not written to output.
        - The JSON is written without indentation for compact output, and
          file permissions are set to 0o664 on Linux/Mac via
          `_set_file_permissions`.
    """

    import os
    import numpy as np
    import json
    import logging
    from pyproj import Transformer

    logger = logging.getLogger('sar_drift_converter')
    
    df_local = df.copy()
    
    # retain only inlier vectors (outlier_category 00 or 01),
    outlier_filter = df_local['outlier_category'].isin(['00', '01'])
    df_local = df_local[outlier_filter].copy()

    if df_local.shape[0] == 0:
        # it might be possible the data frame was labelled as all outliers
        # unlikely, but it needs to be handled
        return
    
    
    # sort by end date so the duplicate guarantees to take the last index
    # that has the latest time stamp
    df_local = df_local.sort_values('date_end', ascending=True)
    
    # two vectors can have slightly different lon/lat but map to
    # the same 12.5 km grid cell. if so, keep the latest (i, j) grid cell
    lons = df_local['longitude_1'].to_numpy()
    lats = df_local['latitude_1'].to_numpy()

    if config['epsg'] == 3413:
        lons_normalized = np.where(lons < 0, lons + 360, lons)
        i, j = _polar_lonlat_to_ij(
            lons_normalized, lats, grid_size=12.5, hemisphere='north'
        )
        RES = 12_500.0
        _, imax, jmax, xmin, ymin = _grid_params(12.5, NORTH)
        x_snapped = (xmin * 1000) + RES * i
        y_snapped = (ymin * 1000) + RES * (jmax - 1 - j)
    elif config['epsg'] == 6931:
        i, j = _ease2_lonlat_to_ij(lons, lats, config)
        RES = 12_500.0
        x_snapped = -9_000_000.0 + RES * i + RES / 2
        y_snapped =  9_000_000.0 - RES * j - RES / 2

    # back-project snapped cell centers to EPSG:4326 for Leaflet
    tf_inv = Transformer.from_crs(
        f'EPSG:{config["epsg"]}', 'EPSG:4326', always_xy=True
    )
    lon1_snapped, lat1_snapped = tf_inv.transform(x_snapped, y_snapped)

    # compute end point from snapped origin + displacement, then back-project
    x2_snapped = x_snapped + df_local['sea_ice_x_displacement'].to_numpy()
    y2_snapped = y_snapped + df_local['sea_ice_y_displacement'].to_numpy()
    lon2_snapped, lat2_snapped = tf_inv.transform(x2_snapped, y2_snapped)

    df_local['_grid_i'] = i
    df_local['_grid_j'] = j
    df_local['longitude_1'] = lon1_snapped
    df_local['latitude_1'] = lat1_snapped
    df_local['longitude_2'] = lon2_snapped
    df_local['latitude_2'] = lat2_snapped

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
            float(np.round(row.longitude_1, config['coordinate_precision'])),
            float(np.round(row.latitude_1,config['coordinate_precision'])),
            float(np.round(row.longitude_2, config['coordinate_precision'])),
            float(np.round(row.latitude_2, config['coordinate_precision'])),
            float(np.round(row.sea_ice_speed_kmdy, config['speed_precision'])),
            float(np.round(
                row.direction_of_sea_ice_displacement,
                config['bearing_precision']
            ))
        ]
        for row in df_local.itertuples(index=False)
    ]

    payload = {
        'date1': date1,
        'date2': date2,
        'count': len(vectors),
        'vectors': vectors
    }

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(payload, f, separators=(',', ':'))                


    # set Linux/Mac permissions on file    
    _set_linux_permissions(json_path)
    
    logger.info(f'Created JSON {json_path}')
    
    
    # update available dates
    date1_key = date1.replace('-', '')  # "YYYYMMDD"
    date2_key = date2.replace('-', '')  # "YYYYMMDD"
    
    if os.path.exists(available_dates_path):
        with open(available_dates_path, 'r', encoding='utf-8') as f:
            available_dates = json.load(f)
        if not isinstance(available_dates, dict):
            available_dates = {}
    else:
        available_dates = {}
    
    if available_dates.get(date1_key) != date2_key:
        available_dates[date1_key] = date2_key
        with open(available_dates_path, 'w', encoding='utf-8') as f:
            json.dump(
                dict(sorted(available_dates.items())),
                f,
                separators=(',', ':')
            )
    
        # set Linux/Mac permissions on file
        _set_linux_permissions(available_dates_path)
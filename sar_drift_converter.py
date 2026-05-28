# -*- coding: utf-8 -*-
"""
******************************************************************************

 Project:     SAR Drift Converter
 Purpose:     Create shape file package (.gpkg) and NetCDF file (.nc) from the
              SAR drift daily file. This script allows the data to be
              visualized in QGIS or any program that can read NetCDF
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


def setup_logger(output_dir):
    """
    Configure and return a file-based logger for the SAR drift converter run.

    Creates a timestamped log file in the specified output directory and
    attaches a file handler to the 'sar_drift_converter' logger. Each run
    produces a uniquely named log file based on the UTC time at invocation.

    Args:
        output_dir (str): Directory where the log file will be written.
                          Must exist prior to calling this function.

    Returns:
        tuple:
            - logger (logging.Logger): Configured logger instance named
              'sar_drift_converter', set to INFO level. Retrieve in any
              module via `logging.getLogger('sar_drift_converter')`.
            - log_path (str): Full path to the log file created, formatted
              as `<output_dir>/run_YYYYMMDD_HHMMSS.log` in UTC.

    Notes:
        - Log records follow the format:
          `YYYY-MM-DD HH:MM:SS,mmm | LEVEL | message`
        - The logger is retrieved by name, so subsequent calls with the same
          process will return the same logger instance and append an
          additional file handler. This function should only be called once
          per run.
        - Only a file handler is attached; no console (stream) handler is
          added, so log output will not appear in stdout unless a handler is
          added separately elsewhere.
    """
    
    import os
    import logging
    from datetime import datetime
    
    log_path = os.path.join(
        output_dir,
        f"run_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.log"
    )
    logger = logging.getLogger('sar_drift_converter')
    logger.setLevel(logging.INFO)

    # file handler
    fh = logging.FileHandler(log_path)
    fh.setLevel(logging.INFO)


    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
    fh.setFormatter(formatter)

    logger.addHandler(fh)

    return logger, log_path


def read_json_config():
    """
    Parse and validate configuration for SAR Drift Output Generator.

    Reads a JSON config file specified via the `-c` / `--config_file`
    command-line argument and validates its contents against a strict schema.
    Ensures all required input files and directories exist, validates types
    and value ranges for each parameter, and merges algorithm constants from
    `constants.py` into the returned config dictionary.

    Expected JSON keys (must match exactly):
        - "sar_drift_directory"   (str):   Path to directory containing
                                           multiple SAR drift delimited files
                                           for batch processing.
        - "sar_drift_filename"    (str):   Path to a single SAR drift
                                           delimited text file.
        - "uw_iabp_buoy_filename" (str):   Path to downloaded buoy data.
        - "sar_drift_data_url"    (str):   URL that hosts SAR drift gfilter
                                           txt files.
        - "uw_iabp_buoy_url"      (str):   URL that hosts UQ IABP buoy data
        - "uw_iabp_buoy_tables"   (str):   .JS file posted online with active
                                           buoys.
        - "netcdf_cdl_file"       (str):   Path to the base CDL file used for
                                           NetCDF metadata. The EPSG-specific
                                           variant is resolved at runtime by
                                           _set_metadata().
        - "netcdf_template_file"  (str):   Path to NetCDF template file on
                                           which scenes will be built.
        - "html_vector_template"  (str):   Path to HTML file that has the code
                                           to display vectors as interactive
                                           quivers with outliers.
        - "html_index_template"   (str):   Template index.html file for
                                           directory listing page.
        - "webpage_folders"       (list):  All of the supporting utilities for
                                           the index.html file to properly
                                           display.
        - "geojson_templates"     (list):  All of the geojson files that get
                                           loaded by HTML interactive map
        - "outlier_qml_file"      (str):   Path to QML file that applies
                                           outlier category styles to
                                           GeoPackages when opened in QGIS.
                                           Used for level '02'.
        - "graduated_qml_file"    (str):   Path to QML file that applies
                                           graduated vector styles to
                                           GeoPackages when opened in QGIS.
                                           Used for all levels other than '02'.
        - "buoy_dir"              (str):   Directory containing dowloaded buoy
                                           data.
        - "meta_dir"              (str):   Directory for template files needed
                                           during processing.
        - "output_dir"            (str):   Parent directory for all processing
                                           output. Per-level subdirectories
                                           are created beneath this path by
                                           create_level_output() before files
                                           are finalized to `file_server`.
                                           Typically set to "level_output".
        - "log_dir"               (str):   Directory for the run log file.
                                           Cleared at the start of each script
                                           run and recreated with a fresh
                                           timestamped log file.
        - "file_server"           (str):   Path to where output files will be
                                           saved and retrieved from the
                                           PolarWatch STAC host server.
        - "clear_output_dir"      (bool):  Remove output directory and all
                                           contents from previous runs.
        - "overwrite"             (bool):  Overwrite files already created on
                                           the file server.
        - "reprocess_days"        (int):   Number of days to overwrite
                                           previously created data files.
        - "batch_process"         (bool):  If True, process all files in
                                           `sar_drift_directory`; if False,
                                           process single `sar_drift_filename`.
        - "delimiter"             (str):   Field separator in the input
                                           file (e.g., ",", "\\t").
        - "verbose"               (bool):  Print detailed parameter info to
                                           the console.
        - "version"               (str):   Version of application.

    Keys beginning with "_comment" are permitted in the JSON file and are
    silently ignored during validation.

    Command-line arguments:
        -c, --config_file: Path to a JSON file with all required configuration.

    Returns:
        dict: Validated configuration dictionary with normalized paths and
              outlier algorithm constants sourced from `constants.py`.
              Key highlights:
              - 'sar_drift_directory':      normalized path (batch mode)
              - 'sar_drift_file':           normalized path (single-file mode)
              - 'netcdf_cdl_file':          normalized path to base CDL file
              - 'netcdf_template_file':     normalized path to NetCDF template
              - 'outlier_qml_file':         normalized path to outlier QML
              - 'graduated_qml_file':       normalized path to graduated QML
              - 'ignore_vector_threshold':  sourced from constants.py
              - 'z_score_level':            sourced from constants.py
              - 'chi_square_level':         sourced from constants.py
              - 'neighbor_radius_km':       sourced from constants.py
              - 'min_neighbors':            sourced from constants.py
              - 'md_min_neighbors':         sourced from constants.py
              - 'outlier_passes':           sourced from constants.py
              - 'bearing_precision':        sourced from constants.py
              - 'speed_precision':          sourced from constants.py
              - 'displacement_precision':   sourced from constants.py
              - 'coordinate_precision':     sourced from constants.py

    Raises:
        SystemExit: If any of the following occur:
            - Config file argument is missing or the file cannot be opened.
            - Required keys are absent or unexpected keys are present.
            - Required files or directories do not exist on disk.
            - Parameter types are invalid (e.g., non-boolean for bool field).
            - Numeric parameters are out of valid range.

    Example:
        $ python sar_drift_converter.py -c config.json
    """

    import util
    import argparse
    import os
    import json
    from constants import (
        IGNORE_VECTOR_THRESHOLD,
        Z_SCORE_LEVEL,
        CHI_SQUARE_LEVEL,
        NEIGHBOR_RADIUS_KM,
        MIN_NEIGHBORS,
        MD_MIN_NEIGHBORS,
        OUTLIER_PASSES,
        BEARING_PRECISION,
        SPEED_PRECISION,
        DISPLACEMENT_PRECISION,
        COORDINATE_PRECISION
    )

    parser = argparse.ArgumentParser(description=(
        'Converts SAR drift data to NetCDF and/or GeoPackage and/or PNG files.'
        )
    )
    parser.add_argument('-c', '--config_file', type=str, action='store',
                        help='Path to config JSON file')
    args = parser.parse_args()
    if not args.config_file:
        util.error_msg('Missing or empty config file argument')

    config_file = os.path.normpath(args.config_file)
    with open(config_file, 'r') as f:
        config = json.load(f)

    # Key validation — strip comment keys before comparison
    comment_keys = {k for k in config.keys() if k.startswith('_comment')}
    config_keys_no_comments = set(config.keys()) - comment_keys

    required_json_keys = {
        "sar_drift_directory", "sar_drift_filename", "uw_iabp_buoy_filename",
        "sar_drift_data_url", "uw_iabp_buoy_url", "uw_iabp_buoy_tables",
        "netcdf_cdl_file", "netcdf_template_file", "html_vector_template",
        "html_index_template", "webpage_folders", "geojson_templates",
        "outlier_qml_file", "graduated_qml_file",  "output_dir", "log_dir",
        "buoy_dir", "meta_dir", "file_server", "clear_output_dir",
        "batch_process", "overwrite", "reprocess_days", "delimiter",
        "verbose", "version"
    }

    missing = required_json_keys - config_keys_no_comments
    extra   = config_keys_no_comments - required_json_keys
    if missing:
        util.error_msg(
            f"Missing required keys in {config_file}: {', '.join(missing)}"
        )
    if extra:
        util.error_msg(
            f"Unexpected keys in {config_file}: {', '.join(extra)}"
        )

    # define schema
    # (key, expected_type, min_value_or_None, allow_zero)
    schema = [
        ("batch_process",            bool,  None, None),
        ("clear_output_dir",         bool,  None, None),
        ("overwrite"       ,         bool,  None, None),
        ("reprocess_days",           int,  None, None),
        ("verbose",                  bool,  None, None)
    ]

    for key, expected_type, min_val, allow_zero in schema:
        val = config[key]
        if not isinstance(val, expected_type):
            util.error_msg(
                f'`{key}` must be {expected_type.__name__}, '
                f'got {type(val).__name__}'
            )
        if min_val is not None and val < min_val:
            util.error_msg(f'`{key} = {val}` must be >= {min_val}')
        config[key] = expected_type(val)

    # path resolution and existence checks
    batch_process = config['batch_process']
    path_checks = [
        ('sar_drift_directory', None, batch_process),
        (
            'sar_drift_filename',
            config['sar_drift_directory'],
            not batch_process
        ),
        ('netcdf_template_file',  config['meta_dir'], True),
        ('html_vector_template', config['meta_dir'], True),
        ('html_index_template', config['meta_dir'], True),
        ('outlier_qml_file', config['meta_dir'], True),
        ('graduated_qml_file', config['meta_dir'], True),
        
    ]
    resolved_paths = {}
    for key_name, dir_prefix, must_exist in path_checks:
        path = os.path.normpath(config[key_name])
        if dir_prefix:
            path = os.path.join(dir_prefix, path)
        if must_exist and not os.path.exists(path):
            util.error_msg(f"Cannot find `{key_name}`: `{path}`")
        resolved_paths[key_name] = path

    # Delimiter decode (\t etc.)
    delimiter = config['delimiter'].encode().decode('unicode_escape')

    # Build final config — output_dir is set by create_level_output()
    config = {
        **resolved_paths,
        'netcdf_cdl_file':         config['netcdf_cdl_file'],
        'uw_iabp_buoy_filename':   config['uw_iabp_buoy_filename'],
        'buoy_dir':                config['buoy_dir'],
        'meta_dir':                config['meta_dir'],
        'output_dir':              config['output_dir'],
        'log_dir':                 config['log_dir'],
        'file_server':             config['file_server'],
        'webpage_folders':         config['webpage_folders'],
        'geojson_templates':       config['geojson_templates'],
        'sar_drift_data_url':      config['sar_drift_data_url'],
        'uw_iabp_buoy_url':        config['uw_iabp_buoy_url'],
        'uw_iabp_buoy_tables':     config['uw_iabp_buoy_tables'],
        'clear_output_dir':        config['clear_output_dir'],
        'batch_process':           config['batch_process'],
        'overwrite':               config['overwrite'],
        'reprocess_days':          config['reprocess_days'],
        'delimiter':               delimiter,
        'ignore_vector_threshold': IGNORE_VECTOR_THRESHOLD,
        'z_score_level':           Z_SCORE_LEVEL,
        'chi_square_level':        CHI_SQUARE_LEVEL,
        'neighbor_radius_km':      NEIGHBOR_RADIUS_KM,
        'min_neighbors':           MIN_NEIGHBORS,
        'md_min_neighbors':        MD_MIN_NEIGHBORS,
        'outlier_passes':          OUTLIER_PASSES,
        'bearing_precision':       BEARING_PRECISION,
        'speed_precision':         SPEED_PRECISION,
        'displacement_precision':  DISPLACEMENT_PRECISION,
        'coordinate_precision':    COORDINATE_PRECISION,
        'verbose':                 config['verbose'],
        'version':                 config['version']
    }

    # echo
    if config['verbose']:
        labels = {
            'sar_drift_directory':           'sar drift directory',
            'sar_drift_filename':            'sar drift file name',
            'uw_iabp_buoy_filename':         'UW IABP buoy filename',
            'sar_drift_data_url':            'SAR drift data URL',
            'uw_iabp_buoy_url':              'UW IABP buoy data URL',
            'uw_iabp_buoy_tables':           'UW IABP buoy tables',
            'netcdf_cdl_file':               'NetCDF CDL file',
            'netcdf_template_file':          'NetCDF template file',
            'html_vector_template':          'HTML vector template file',
            'html_index_template':           'index.html template',
            'webpage_folders':               'Supporting index.html files',
            'geojson_templates':             'GeoJSON template files',
            'outlier_qml_file':              'outlier qml file',
            'graduated_qml_file':            'graduated qml file',
            'buoy_dir':                      'buoy data directory',
            'meta_dir':                      'metadata directory',
            'output_dir':                    'output directory',
            'log_dir':                       'log directory',
            'file_server':                   'file server',
            'clear_output_dir':              'clear output directory',
            'batch_process':                 'batch process',
            'overwrite':                     'overwrite',
            'reprocess_days':                'reprocess days',
            'delimiter':                     'delimiter',
            'ignore_vector_threshold':       'ignore vector threshold',
            'z_score_level':                 'z-score level',
            'chi_square_level':              'chi-square level',
            'neighbor_radius_km':            'neighbor radius (km)',
            'min_neighbors':                 'minimum neighbors',
            'md_min_neighbors':              'MD minimum neighbors',
            'outlier_passes':                'outlier passes',
            'bearing_precision':             'bearing precision',
            'speed_precision':               'speed precision',
            'displacement_precision':        'displacement precision',
            'coordinate_precision':          'coordinate precision',
            'version':                       'version'
        }
        lines = ["CONF PARAMS:"]
        for key, label in labels.items():
            lines.append(f"  {label:<25} {config[key]}")
        print('\n'.join(lines))

    return config
    
    
def create_scene_output(day, df_day, config, template_ds, exists):
    """
    Process all File1/File2 scene pairs within a single day's DataFrame and
    produce per-scene output files.

    For each scene pair, saves a formatted CSV, runs outlier detection, and
    writes a per-scene NetCDF file. The post-outlier-detection rows from all
    scenes are accumulated and returned as a combined DataFrame for the caller
    to use when producing daily-level GeoPackage and vector HTML/JSON outputs.

    Args:
        day (str): Date string for the current processing day
                   (format: 'YYYYMMDD'); used in log messages.
        df_day (pandas.DataFrame): All drift observations for the current day,
            grouped upstream by `date_range`. Expected columns include all
            fields produced by `read_sar_drift_data_file` and
            `filter_input_data`, including 'scene_id', 'date_start',
            and 'date_end'.
        config (dict): Configuration dictionary. Must include:
                - 'formatted_data_dir' (str): Directory for per-scene
                                              formatted CSV output.
                - 'nc_dir' (str): Directory for NetCDF output.
                - 'level' (str): Processing level ('00'–'03'); controls
                                 outlier detection behaviour and which
                                 output types the caller will produce.
                - 'neighbor_radius_km' (float): Search radius for outlier
                                                neighbor lookup.
                - 'min_neighbors' (int): Minimum neighbors for z-score
                                         confidence.
                - 'md_min_neighbors' (int): Minimum neighbors for
                                            Mahalanobis confidence.
                - 'z_score_level' (float): Z-score outlier threshold.
                - 'chi_square_level' (float): Chi-square threshold for
                                              Mahalanobis distance.
                - 'outlier_passes' (int): Number of outlier detection
                                          iterations.
        template_ds (xarray.Dataset): NetCDF template dataset passed
                                      directly to `util.create_netcdf`.
        exists (dict): Output existence flags as returned by
            `check_existing_files`. The following keys are used:
                - `nc_scenes` (bool): If True and `nc_daily` is also True,
                  per-scene NetCDF files are not written since neither
                  daily NetCDF variant needs them. If either is False,
                  per-scene NetCDF files are written because both daily
                  NetCDF variants depend on them as inputs to
                  `util.combine_daily_netcdf_files`.
                - `nc_daily` (bool): See `nc_scenes` above.
            Outlier detection always runs regardless of these flags since
            `df_scenes` is required by the caller for GeoPackage and
            vector HTML/JSON outputs.

    Returns:
        dict: Summary of the day's scene processing, containing:
                - 'scenes' (int): Total number of File1/File2 scene pairs
                                  processed.
                - 'df_scenes' (pandas.DataFrame): Combined DataFrame of all
                                                  per-scene rows after outlier
                                                  detection has been applied.
                                                  Intended for use by the
                                                  caller to produce a single
                                                  daily GeoPackage and vector
                                                  HTML/JSON across all scenes.
                                                  Empty DataFrame if no scenes
                                                  produced rows.
                - 'start_date' (pandas.Timestamp): Minimum `date_start`
                                                   across all scenes,
                                                   pre-computed from `df_day`
                                                   before the scene loop.
                - 'end_date' (pandas.Timestamp): Maximum `date_end` across
                                                 all scenes, pre-computed
                                                 from `df_day` before the
                                                 scene loop.
                - 'nc_files' (list[str]): Paths of successfully written
                                          per-scene NetCDF files.

    Notes:
        - `start_date` and `end_date` in the return dict are derived from the
          full `df_day` DataFrame before the scene loop runs, not accumulated
          incrementally across scenes. Any scene's min/max is guaranteed to
          fall within the day-level bounds already established, so per-scene
          comparisons are not required.
        - A formatted CSV is written for every scene unconditionally, before
          outlier detection is applied.
        - NetCDF output file paths are appended to `nc_files` only when
          `util.create_netcdf` returns a non-None path. This prevents
          referencing files that were never created due to all vectors in a
          scene being filtered as outliers.
        - The `scene_i_j` dictionary is populated in-place by
          `util.create_netcdf` and maps each `scene_id` to its list of
          (i, j) grid index pairs.
        - Per OSI SAF convention, the reference date in scene filenames
          corresponds to the end of the observation period. Where multiple
          scene pairs exist within a day, the overall start and end timestamps
          are the minimum `date_start` and maximum `date_end` across all
          scenes.
        - `df_scenes` is assembled by concatenating each per-scene DataFrame
          after outlier detection. The caller is responsible for producing
          daily-level GeoPackage and vector HTML/JSON outputs from this
          combined DataFrame rather than concatenating per-scene output files.
    """

    import util
    import os
    import logging
    import pandas as pd

    logger = logging.getLogger('sar_drift_converter')

    scene_frames = []
    unique_keys = set()

    daily_start_date = pd.to_datetime(df_day['date_start'].min())
    daily_end_date   = pd.to_datetime(df_day['date_end'].max())

    scene_count = 0
    for scene_id, df_scene in df_day.groupby('scene_id'):

        # skip scene that is not unique though pair name is unique
        unique_pair_key = df_scene['_unique_pair_key'].iloc[0]
        if unique_pair_key in unique_keys:
            logger.info(
                f"Ignoring Scene {scene_id} | "
                f"duplicate unique scene key {unique_pair_key} | "
                f"date_range={day}"
            )
            continue            
        
        # mark this key as seen
        unique_keys.add(unique_pair_key)  

        scene_count += 1
        
        logger.info(
            f"Scene {scene_id} | "
            f"rows={len(df_scene)} | "
            f"date_range={day} | "
            f"unique pair key={unique_pair_key}"
        )

        if config['level'] == '00':
            output_path = os.path.join(
                config['formatted_data_dir'],
                f"formatted_{scene_id}.csv"
            )
            df_scene.to_csv(output_path, index=False)

        df_scene = util.outlier_search(
            df=df_scene,
            config=config,
            base_name=scene_id,
            radius_km=config['neighbor_radius_km'],
            min_neighbors=config['min_neighbors'],
            md_neighbors=config['md_min_neighbors'],
            z_score_level=config['z_score_level'],
            chi_square_level=config['chi_square_level'],
            passes=config['outlier_passes']
        )
        scene_frames.append(df_scene)

    
    if scene_frames:
        df_scenes = pd.concat(scene_frames, ignore_index=True)
    else:
        df_scenes = pd.DataFrame()


    return {
        'scenes':     scene_count,
        'df_scenes':  df_scenes,
        'start_date': daily_start_date,
        'end_date':   daily_end_date
    }
            
    
def create_daily_output(scene_output, config, template_ds, exists):
    """
    Combine all per-scene output files for a single day into daily products
    and write them to the file server directory.

    Takes the per-scene results produced by `create_scene_output` and writes
    day-level NetCDF, GeoPackage, vector HTML/JSON, and formatted CSV files.
    Two NetCDF variants are always produced: a multi-layered file with one
    time layer per scene pair, and a single-layer daily summary. GeoPackage
    and vector HTML/JSON outputs are produced based on the configured
    processing level. Two formatted CSVs are always written unconditionally:
    one of the raw day's observations and one of the post-outlier-detection
    rows with processing codes.

    Args:
        scene_output (dict): Return value from `create_scene_output` for this
            day. Expected keys:
                - 'start_date' (pandas.Timestamp): Minimum `date_start`
                                                   across all scenes.
                - 'end_date' (pandas.Timestamp): Maximum `date_end` across
                                                 all scenes.
                - 'scenes' (int): Number of scene pairs processed.
                - 'df_scenes' (pandas.DataFrame): Combined DataFrame of all
                                                  per-scene rows after outlier
                                                  detection; used directly as
                                                  input to
                                                  `util.create_shape_package`
                                                  and
                                                  `util.create_vector
                                                  _html_and_json`,
                                                  and written to a formatted
                                                  CSV with processing codes
                                                  unconditionally.
                - 'nc_files' (list[str]): Paths of successfully written
                                          per-scene NetCDF files.
                - 'gpkg_files' (list[str]): Paths of successfully written
                                            per-scene GeoPackage files
                                            (unused by this function;
                                            retained for caller inspection).
                - 'html_files' (list[str]): Paths of successfully written
                                            per-scene HTML files (unused by
                                            this function; retained for
                                            caller inspection).
        config (dict): Configuration dictionary. Must include:
                - 'file_server' (str): Root path of the PolarWatch STAC file
                  server. Daily outputs are written to subdirectories
                  structured as `<file_server>/<epsg>/<level>/<year>/<type>/`.
                - 'level' (str): Processing level; controls which daily output
                  types are produced:
                      '00': NetCDF (multi-layer + single), GeoPackage,
                            vector HTML/JSON
                      '01': NetCDF (multi-layer + single)
                      '02': NetCDF (multi-layer + single), GeoPackage
                      '03': NetCDF (multi-layer + single), GeoPackage,
                            vector HTML/JSON
                - 'epsg' (int): EPSG code included in output filenames and
                                used as a top-level subdirectory under
                                `file_server`.
                - 'version' (str): Version string included in output
                                   filenames.
                - 'formatted_data_dir' (str): Local directory for the
                                              formatted daily CSVs.
        template_ds (xarray.Dataset): NetCDF template dataset passed directly
                                      to `util.combine_daily_netcdf_files`.

    Returns:
        None

    Notes:
        - Output filenames follow the convention:
            `SIVelocity_SAR_<start>_<end>_<type>_12km_NH_<epsg>_
            PL<level>_v<version>.<ext>`
          where `<type>` is `scenes` for the multi-layered NetCDF and
          `daily` for all other output types.
        - Output directories under `file_server` are created if they do not
          already exist, structured as
          `<file_server>/<epsg>/<level>/<year>/<type>/` where `<level>` is
          the full processing level label (e.g. 'Processing Level - 03
          (PL03)') and `<year>` is the four-digit start year.
        - The GeoPackage and vector HTML/JSON are produced directly from
          `scene_output['df_scenes']` rather than by merging per-scene
          output files, so each daily product is generated in a single call
          and reflects post-outlier-detection data across all scenes.
        - The vector HTML output is accompanied by a JSON data file written
          to a `data/` subdirectory alongside the HTML file.
        - Two formatted CSVs are written unconditionally to
          `config['formatted_data_dir']`: `<start>_<end>_raw.csv` containing
          `df_day` as received, and `<start>_<end>_processing_codes.csv`
          containing `scene_output['df_scenes']` with outlier codes applied.
    """

    import util
    import os
    import logging

    logger = logging.getLogger('sar_drift_converter')

    daily_start_date_str = scene_output['start_date'].strftime("%Y%m%d")
    daily_end_date_str = scene_output['end_date'].strftime("%Y%m%d")
    epsg = str(config['epsg'])
    lvl = f"Processing Level - {config['level']} (PL{config['level']})"
    yr = str(daily_start_date_str[0:4])


    # multiple-layered netcdf
    if not exists['nc_scenes']:
        output_dir = os.path.join(
            config['file_server'], epsg, lvl, yr, 'nc'
        )
        os.makedirs(output_dir, exist_ok=True)
        scenes_nc_path = os.path.join(
            output_dir,
            f"SIVelocity_SAR_{daily_start_date_str}_{daily_end_date_str}"
            f"_scenes_12km_NH_{config['epsg']}_PL{config['level']}"
            f"_v{config['version']}.nc"
        )
        util.create_netcdf(
            df=scene_output['df_scenes'],
            nc_path=scenes_nc_path,
            config=config,
            template_ds=template_ds,
            multi_layered=True
        )


    # single-layer netcdf
    if not exists['nc_daily']:
        output_dir = os.path.join(
            config['file_server'], epsg, lvl, yr, 'nc'
        )
        os.makedirs(output_dir, exist_ok=True)
        daily_nc_path = os.path.join(
            output_dir,
            f"SIVelocity_SAR_{daily_start_date_str}_{daily_end_date_str}"
            f"_daily_12km_NH_{config['epsg']}_PL{config['level']}"
            f"_v{config['version']}.nc"
        )
        util.create_netcdf(
            df=scene_output['df_scenes'],
            nc_path=daily_nc_path,
            config=config,
            template_ds=template_ds,
            multi_layered=False
        )


    # GeoPackage
    if not exists['gpkg']:
        output_dir = os.path.join(config['file_server'], epsg, lvl, yr, 'gpkg')
        os.makedirs(output_dir, exist_ok=True)
        gpkg_path = os.path.join(
            output_dir,
            f"SIVelocity_SAR_{daily_start_date_str}_{daily_end_date_str}"
            f"_daily_12km_NH_{config['epsg']}_PL{config['level']}"
            f"_v{config['version']}.gpkg"
        )
        util.create_shape_package(
            df=scene_output['df_scenes'],
            gpkg_path=gpkg_path,
            config=config
        )


    # JSON vectors and HTML viewer
    if not exists['json']:
        output_dir = os.path.join(config['file_server'], epsg, lvl)
        data_dir = os.path.join(output_dir, "data")
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(data_dir, exist_ok=True)

        html_path = os.path.join(
            output_dir,
            os.path.basename(config['html_vector_template'])
        )
                
        si_json_path = os.path.join(
            data_dir, f"si_velocity_{daily_start_date_str}.json"
        )
        buoy_json_path = os.path.join(
            data_dir, f"buoy_velocity_{daily_start_date_str}.json"
        )
        available_dates_path = os.path.join(
            data_dir, 'available_dates.json'
        )
        
        util.create_vector_html_and_json(
            df=scene_output['df_scenes'],
            html_path=html_path,
            data_dir=data_dir,
            si_json_path=si_json_path,
            buoy_json_path=buoy_json_path,
            available_dates_path=available_dates_path,
            config=config
        )


    logger.info(
        f"Day {daily_start_date_str}_{daily_end_date_str} complete | "
        f"scenes={scene_output['scenes']}"
    )


def create_level_output(df_all, config):
    """
    Execute the full daily processing workflow for one level/EPSG combination.

    Receives a pre-projected DataFrame for a single EPSG, applies quality
    filtering, groups observations by calendar day, and produces all
    configured output files for each day. This function is called once per
    level/EPSG combination by `process_level_output`.

    Args:
        df_all (pandas.DataFrame): Pre-projected combined DataFrame for the
            target EPSG, as returned by `util._apply_projection`. Must
            contain all columns produced by `combine_into_dataframe` and
            `_apply_projection`, including projected coordinates `X1`, `Y1`,
            `X2`, `Y2`, displacement, speed, and bearing columns.
        config (dict): Configuration dictionary containing all keys from
            `read_json_config`, plus:
                - 'level' (str): Processing level set by the caller
                  ('00'–'03').
                - 'epsg' (int): Target projected CRS code set by the
                  caller (3413 or 6931).
                - 'start_date' (date): Minimum date_start across all
                  input data; set by the caller for levels '00' and '03'.
                - 'end_date' (date): Maximum date_start across all input
                  data; set by the caller for levels '00' and '03'.
                - 'buoy_drift' (pandas.DataFrame or None): Loaded buoy
                  drift DataFrame for levels '00' and '03'; None otherwise.

    Workflow:
        1. Validate `level` and `epsg` from config.
        2. Set up the output directory tree under `output_dir/<level>/`
           and optionally clear it if `config['clear_output_dir']` is True.
        3. Open the NetCDF template specified by
           `config['netcdf_template_file']` to provide the target grid.
        4. Apply per-row and scene-level quality filters via
           `filter_input_data`.
        5. Assign a `date_range` column (YYYYMMDD of `date_start`).
        6. For each calendar day, call `_check_existing_files` to determine
           which outputs need to be written. Days within `reprocess_days`
           of today or where `overwrite` is True are always reprocessed.
           Days where all outputs already exist are skipped entirely.
        7. For each day requiring processing, call `create_scene_output`
           to run outlier detection and accumulate per-scene rows into
           `df_scenes`, then call `create_daily_output` to write all
           daily output files.
        8. For level '00', write raw and processing-codes CSVs per day.
        9. Log total elapsed run time for this level/EPSG on completion.

    Returns:
        None

    Notes:
        - Progress across days is displayed via a `tqdm` progress bar.
        - `output_dir`, `formatted_data_dir`, `nc_dir`, and
          `filtered_data_dir` are written into `config` by this function
          as subdirectories of `output_dir/<level>/`.
        - A `gc.collect()` call is made after each day to release memory
          held by per-scene DataFrames and outlier detection columns.
    """
    
    import util
    import os
    import shutil
    from datetime import datetime
    from tqdm import tqdm
    import logging
    import pandas as pd
    import xarray as xr
    import gc

    
    run_start = datetime.utcnow()


    # epsg validation
    if config['epsg'] not in [3413, 6931]:
        util.error_msg('`epsg` must be `3413` or `6931`')
        
    # level validation
    if config['level'] not in ['00', '01', '02', '03']:
        util.error_msg('`level` must be one of: `00`, `01`, `02`, `03`')
    


    # log activity
    logger = logging.getLogger('sar_drift_converter')
    logger.info(
        f"Run started | config level={config['level']} | "
        f"EPSG={config['epsg']} | {run_start}"
    )

        
    # Output directory setup
    config['output_dir'] = os.path.normpath(
        os.path.join('level_output', f"{config['level']}")
    )
    if os.path.exists(config['output_dir']) and config['clear_output_dir']:
        print(f"Clearing output directory --> {config['output_dir']}")
        shutil.rmtree(config['output_dir'])
        

    subdirs = ['filtered_data', 'formatted_data', 'nc']    
    for name in subdirs:
        path = os.path.join(config['output_dir'], name)
        os.makedirs(path, exist_ok=True)
        config[f'{name}_dir'] = path
        
        
    # load NSIDC polar stereographic EPSG:3411 NetCDF template
    with xr.open_dataset(config['netcdf_template_file']) as ds:
        template_ds = ds.load()

    
    # apply row-level filters per File1/File2 scene group
    df_all = util.filter_input_data(df_all, config)
    
    
    # define unique pair key
    f1 = df_all['File1'].str.split('_')
    f2 = df_all['File2'].str.split('_')
    df_all['_unique_pair_key'] = (
        f1.str[0] + '_' + f1.str[8] + '_' + f2.str[0] + '_' + f2.str[8]
    )
    del f1, f2

    
    # create date range groups for daily/scene output
    print('Creating groups based on start day...')
    df_all['date_range'] = (
        pd.to_datetime(df_all['date_start']).dt.strftime('%Y%m%d')
    )
    
   
    # create output: group by day, then by scene within each day
    start_days = {}
    for day, df_day in tqdm(
            df_all.groupby('date_range'), "Processing days...", unit='day'
        ):        
        
        logger.info(f"Processing day: {day}")
        
        stub = {
            'start_date': pd.to_datetime(df_day['date_start']).min(),
            'end_date':   pd.to_datetime(df_day['date_end']).max(),
        }

        exists = util._check_existing_files(stub, config)


        if all(exists.values()):
            logger.info(
                f"Skipping {stub['start_date'].strftime('%Y%m%d')}. "
                f"All level {config['level']} outputs already exist"
            )
            continue

        # create scene output with outliers if applicable
        scene_output = create_scene_output(
            day=day,
            df_day=df_day,
            config=config,
            template_ds=template_ds,
            exists=exists
        )

        key = scene_output['start_date'].strftime('%Y%m%d')
        if key not in start_days:
            start_days[key] = ''
        else:
            print(f"Duplicate {key}")
            exit()

                
        # combine all created daily files into one
        create_daily_output(scene_output, config, template_ds, exists)
        

        gc.collect()
        
        
        # write out raw daily data
        if config['level'] == '00':
            daily_start_date_str = (
                scene_output['start_date'].strftime("%Y%m%d")
            )
            daily_end_date_str = (
                scene_output['end_date'].strftime("%Y%m%d")
            )
            
            # formatted CSVs
            output_path = os.path.join(
                config['formatted_data_dir'],
                f"{daily_start_date_str}_{daily_end_date_str}_raw.csv"
            )
            df_day.to_csv(output_path, index=False)
            
            
            output_path = os.path.join(
                config['formatted_data_dir'],
                f"{daily_start_date_str}_{daily_end_date_str}_"
                "processing_codes.csv"
            )
            scene_output['df_scenes'].to_csv(output_path, index=False)


    # final log entry
    run_end = datetime.utcnow() 
    elapsed = run_end - run_start
    logger.info(
        f"Run complete | {run_end} | elapsed={elapsed}"
    )
    
    
def process_level_output(test=False):
    """
    Top-level entry point for the SAR drift output generation pipeline.
 
    Parses and validates configuration via `read_json_config()`, compresses
    any existing log files to ZIP archives, initialises a fresh timestamped
    log file, reads all input gfilter files in parallel into a single raw
    DataFrame, applies coordinate projections for each target EPSG, then
    dispatches `create_level_output()` for each level/EPSG combination.
    Logs total elapsed time on completion.
 
    This function is intended to be called only when the script is run
    directly (`__name__ == "__main__"`).
 
    Workflow:
        1. Parse and validate runtime configuration via `read_json_config()`.
        2. Compress any existing `.log` files in `config['log_dir']` to
           `.zip` archives, then initialise a fresh timestamped log file
           via `setup_logger()`.
        3. Glob-match all `.txt`|`.csv` input files from
           `config['sar_drift_directory']` (batch mode) or use the single
           file at `config['sar_drift_filename']` (single-file mode).
        4. Read all input files in parallel into a single raw DataFrame
           (`combine_into_dataframe`). File reads use ProcessPoolExecutor
           across all available CPU cores. Processing halts immediately on
           any file read failure.
        5. Apply EPSG-dependent coordinate projection once per target EPSG
           (`util._apply_projection`), producing one projected DataFrame
           per CRS. EPSGs processed: [3413, 6931]. This step is cheap
           (vectorized numpy/pyproj) compared to file I/O and runs after
           all files are combined.
        6. For each level/EPSG combination, call `create_level_output()`
           with the pre-projected DataFrame for that EPSG.
        7. Log total elapsed run time on completion.
 
    Args:
        test (bool): If True, only processing level '00' is run instead of
            the full production set ('01', '02', '03'). Defaults to
            False.
 
    Notes:
        - Processing levels are hardcoded: ['01', '02', '03'] in
          production, ['00'] in test mode. They are not read from
          `config.json`.
        - EPSG codes are hardcoded as [3413, 6931]. Up to four EPSGs are
          supported without meaningful performance impact since file I/O
          runs only once and projection is applied per EPSG from the
          already-loaded DataFrame.
        - Previous log files are compressed to ZIP before the new log is
          created, preserving run history without accumulating uncompressed
          log files.
        - All level/EPSG combinations share one log file for the run.
          Filter log entries by level or EPSG to isolate output for a
          specific combination.
        - Pyproj CRS configuration is applied at startup via `pyproj_setup`.
        - On Windows, ProcessPoolExecutor uses the `spawn` start method.
          This function must only be called from within a
          `if __name__ == "__main__"` guard to prevent recursive worker
          spawning.
    """
    
    import pyproj_setup
    import util
    import os
    from datetime import datetime
    import numpy as np
    import zipfile
    from glob import glob
    
    
    run_start = datetime.utcnow()
    
    # parse user arguments
    config = read_json_config()
    
    # initialize logger
    os.makedirs(config['log_dir'], exist_ok=True)
    for log_file in glob(os.path.join(config['log_dir'], '*.log')):        
        zip_path = log_file.replace('.log', '.zip')
        print(f'Compressing {log_file}')
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.write(log_file, os.path.basename(log_file))
        os.remove(log_file)
    logger, log_path = setup_logger(config['log_dir'])
    logger.info(
        f"Process started | {run_start}"
    )


    # download recent files
    util._download_sar_drift_files(config)
    
    
    # find files to process
    print("Gathering files to process...")
    files= []
    if config['batch_process']:
        all_files = glob(os.path.join(config['sar_drift_directory'], '*'))
        for file in all_files:
            if ('.txt' in file) or ('.csv' in file):
                files.append(file)
    else:
        files = [config['sar_drift_filename']]
        
    
    logger.info(f"Input directory: {config['sar_drift_directory']}")
    logger.info(f"Found {len(files)} candidate files")
    
    
    # read data files and load them into a data frame
    df_raw = util.combine_into_dataframe(files, config)
    
    # in case supplied data files duplicate individual scene files
    df_raw.drop_duplicates(inplace=True)
    
    # drop any rows where polarization is not HH in the scene
    pol1 = df_raw['File1'].str.extract(r'_([^_]+)_C$')[0]
    pol2 = df_raw['File2'].str.extract(r'_([^_]+)_C$')[0]
    
    hh_mask = (pol1 == 'HH') & (pol2 == 'HH')
    dropped = (~hh_mask).sum()
    logger.info(
        f"Dropped {dropped} observations where HH not in both polarizations"
    )
    df_raw = df_raw[hh_mask].reset_index(drop=True)
    

    epsg_list = [3413, 6931]
    if test:
        processing_levels = ['00']
    else:
        # processing_levels = ['01', '02', '03']
        processing_levels = ['03']
    
    obs_read=df_raw.shape[0]
    total_days=df_raw['date_start'].dt.date.nunique()
    total_scenes=len(np.unique(df_raw[['File1', 'File2']]))
    logger.info(
        f'Input data totals | total observations: {obs_read}; '
        f'total days: {total_days}; total scenes: {total_scenes}'
    )
    
    
    df_by_epsg = {}
    for epsg in epsg_list:
        df_by_epsg[epsg] = util._apply_projection(df_raw, epsg, config)
    
    for level in processing_levels:
        for epsg in epsg_list:
            config['level'] = level
            config['epsg'] = epsg
            if level in ['00', '03']:
                config['start_date'] = df_raw['date_start'].dt.date.min()
                config['end_date'] = df_raw['date_start'].dt.date.max()
                config['buoy_drift'] = util._load_buoy_data(config)
                util._update_interactive_html_files(config, epsg)
            else:
                config['buoy_drift'] = None
            create_level_output(df_by_epsg[epsg], config)


    # update remote data repository
    # util._copy_to_gdrive(config)
    
    
    # final log entry
    run_end = datetime.utcnow() 
    elapsed = run_end - run_start
    logger.info(
        f"Process completed | {run_end} | elapsed={elapsed}"
    )
    
    
if __name__ == "__main__":
    process_level_output()
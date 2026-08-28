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


def setup_logger(config):
    """
   Configure and return a file-based logger for the SAR drift converter run.

   Creates a timestamped log file in the configured log directory and
   attaches a file handler to the 'sar_drift_converter' logger. Each run
   produces a uniquely named log file based on the UTC time at invocation.

   Args:
       config (dict): Configuration dictionary. Must include:
               - 'log_dir' (str): Directory where the log file will be
                 written. Must exist prior to calling this function.

   Returns:
       tuple:
           - logger (logging.Logger): Configured logger instance named
             'sar_drift_converter', set to INFO level. Retrieve in any
             module via `logging.getLogger('sar_drift_converter')`.
           - log_path (str): Full path to the log file created, formatted
             as `<log_dir>/run_YYYYMMDD_HHMMSS.log` in UTC.

   Notes:
       - Log records follow the format:
         `YYYY-MM-DD HH:MM:SS,mmm | LEVEL | message`
       - The logger is retrieved by name, so subsequent calls within the
         same process return the same logger instance and append an
         additional file handler. This function should only be called once
         per run.
       - Only a file handler is attached; no console (stream) handler is
         added, so log output does not appear in stdout unless a handler is
         added separately elsewhere.
   """
    
    import os
    import logging
    from datetime import datetime
    
    log_path = os.path.join(
        config['log_dir'],
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
        - "sar_drift_download_directory" (str):  Directory cleared and
                                                 repopulated each run from
                                                 `sar_drift_data_url`
                                                 covering the `reprocess_days`
                                                 window.
        - "sar_drift_manual_directory"  (str):   User-managed directory; never
                                                 cleared by the script. Always
                                                 processed regardless of
                                                 `reprocess_days`.
        - "file_server_3413"            (list):  Path components for the
                                                 EPSG:3413 root output path.
        - "file_server_6931"            (list):  Path components for the
                                                 EPSG:6931 root output path.
        - "json_dir"                    (list):  Directory where the JSON
                                                 directories files are located.
                                                 written.                                                 
        - "sar_drift_data_url"          (str):   URL hosting SAR drift gfilter
                                                 txt files.
        - "netcdf_cdl_file_3413"        (str):   Path to the CDL file used for
                                                 NetCDF metadata (EPSG:3413).
        - "netcdf_cdl_file_6931"        (str):   Path to the CDL file used for
                                                 NetCDF metadata (EPSG:6931).
        - "outlier_qml_file"            (str):   Path to QML file for outlier
                                                 category styles (level '02').
        - "graduated_qml_file"          (str):   Path to QML file for graduated
                                                 vector styles (all levels
                                                                except '02').
        - "meta_dir"                    (str):   Directory for template files
                                                 needed during processing.
        - "log_dir"                     (str):   Directory for the run log
                                                 file.
        - "overwrite"                   (bool):  Overwrite files already
                                                 created on the file server.
        - "reprocess_days"              (int):   Number of most-recent days to
                                                 always reprocess.
        - "delimiter"                   (str):   Field separator in the input
                                                 file (e.g., ",", "\\t").
        - "verbose"                     (bool):  Print detailed parameter info
                                                 to the console.
        - "version"                     (str):   Version string included in
                                                 output filenames.

    Keys beginning with "_comment" are permitted in the JSON file and are
    silently ignored during validation.

    Command-line arguments:
        -c, --config_file: Path to a JSON file with all required configuration.

    Returns:
        dict: Validated configuration dictionary with normalized paths and
              outlier algorithm constants sourced from `constants.py`.
              Key highlights:
              - 'sar_drift_automated_directory': normalized path to automated
                                                 input directory
              - 'sar_drift_automated_directory': normalized path to manual
                                                 input directory
              - 'netcdf_cdl_file_3413':          normalized path to base CDL
                                                 file
              - 'netcdf_cdl_file_6931':          normalized path to base CDL
                                                 file
              - 'outlier_qml_file':              normalized path to outlier
                                                 QML
              - 'graduated_qml_file':            normalized path to graduated
                                                 QML
              - 'ignore_vector_threshold':       sourced from constants.py
              - 'z_score_level':                 sourced from constants.py
              - 'chi_square_level':              sourced from constants.py
              - 'neighbor_radius_km':            sourced from constants.py
              - 'min_neighbors':                 sourced from constants.py
              - 'md_min_neighbors':              sourced from constants.py
              - 'outlier_passes':                sourced from constants.py
              - 'bearing_precision':             sourced from constants.py
              - 'speed_precision':               sourced from constants.py
              - 'displacement_precision':        sourced from constants.py
              - 'coordinate_precision':          sourced from constants.py

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

    # Key validation (strip comment keys before comparison)
    comment_keys = {k for k in config.keys() if k.startswith('_comment')}
    config_keys_no_comments = set(config.keys()) - comment_keys

    required_json_keys = {
            'sar_drift_download_directory', 'sar_drift_manual_directory',
            'file_server_3413', 'file_server_6931', 'json_dir',
            'sar_drift_data_url', 'netcdf_cdl_file_3413',
            'netcdf_cdl_file_6931', 'outlier_qml_file', 'graduated_qml_file',
            'log_dir', 'meta_dir', 'overwrite', 'reprocess_days', 'delimiter',
            'verbose', 'version'
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
    path_checks = [
        ('sar_drift_download_directory', None, True),
        ('sar_drift_manual_directory', None, True),
        ('netcdf_cdl_file_3413', config['meta_dir'], True),
        ('netcdf_cdl_file_6931', config['meta_dir'], True),
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

    # Build final config (output_dir is set by create_level_output())
    config = {
        **resolved_paths,
        'meta_dir':                config['meta_dir'],
        'log_dir':                 config['log_dir'],
        'file_server_3413':        os.path.join(*config['file_server_3413']),
        'file_server_6931':        os.path.join(*config['file_server_6931']),
        'json_dir':                os.path.join(*config['json_dir']),
        'sar_drift_data_url':      config['sar_drift_data_url'],
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
            'sar_drift_download_directory': 'sar drift download directory',
            'sar_drift_manual_directory':   'sar drift manual directory',
            'file_server_3413':             'file server (EPSG:3413)',
            'file_server_6931':             'file server (EPSG:6931)',
            'json_dir':                     'JSON files directory',
            'sar_drift_data_url':           'SAR drift data URL',
            'netcdf_cdl_file_3413':         'NetCDF CDL file (EPSG:3413)',
            'netcdf_cdl_file_6931':         'NetCDF CDL file (EPSG:6931)',
            'outlier_qml_file':             'outlier qml file',
            'graduated_qml_file':           'graduated qml file',
            'meta_dir':                     'metadata directory',
            'log_dir':                      'log directory',
            'overwrite':                    'overwrite',
            'reprocess_days':               'reprocess days',
            'delimiter':                    'delimiter',
            'ignore_vector_threshold':      'ignore vector threshold',
            'z_score_level':                'z-score level',
            'chi_square_level':             'chi-square level',
            'neighbor_radius_km':           'neighbor radius (km)',
            'min_neighbors':                'minimum neighbors',
            'md_min_neighbors':             'MD minimum neighbors',
            'outlier_passes':               'outlier passes',
            'bearing_precision':            'bearing precision',
            'speed_precision':              'speed precision',
            'displacement_precision':       'displacement precision',
            'coordinate_precision':         'coordinate precision',
            'version':                      'version'
        }
        lines = ["CONF PARAMS:"]
        for key, label in labels.items():
            lines.append(f"  {label:<30} {config[key]}")
        print('\n'.join(lines))

    return config
    
    
def create_scene_output(day, df_day, config, template_ds, exists):
    """
    Process all unique File1/File2 scene pairs within a single day's
    DataFrame and accumulate post-outlier-detection rows for the caller.

    For each scene pair, runs outlier detection and appends the resulting
    rows to a combined DataFrame. Duplicate scene pairs (different scene_id
    but identical sensor/acquisition-seconds key) are skipped. The combined
    DataFrame is returned to the caller, which uses it to produce the
    day-level NetCDF, GeoPackage, and vector JSON outputs.

    Args:
        day (str): Date string for the current processing day
                   (format: 'YYYYMMDD'); used in log messages.
        df_day (pandas.DataFrame): All drift observations for the current
            day, grouped upstream by `date_range`. Expected columns include
            all fields produced by `read_sar_drift_data_file`,
            `_apply_projection`, and `filter_input_data`, plus the
            `_unique_pair_key` column assigned in `create_level_output`.
        config (dict): Configuration dictionary. Must include:
                - 'level' (str): Processing level ('00'–'03'); controls
                                 outlier detection behaviour and, for level
                                 '00', whether per-scene formatted CSVs are
                                 written.
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
                - 'test_output_dir' (str): Directory for per-scene formatted
                                           CSV output; only required for
                                           level '00'.
        template_ds (xarray.Dataset): NetCDF template dataset; accepted for
                                      signature consistency with the caller
                                      but not used directly in this function.
        exists (dict): Output existence flags as returned by
            `_check_existing_files`. Accepted for signature consistency;
            outlier detection always runs regardless of these flags since
            `df_scenes` is required by the caller for all daily outputs.

    Returns:
        dict: Summary of the day's scene processing, containing:
                - 'scenes' (int): Number of unique scene pairs processed
                                  (duplicates excluded).
                - 'df_scenes' (pandas.DataFrame): Combined DataFrame of all
                                                  per-scene rows after outlier
                                                  detection. Empty DataFrame
                                                  if no scenes produced rows.
                - 'start_date' (pandas.Timestamp): Minimum `date_start`
                                                   across the day's
                                                   observations.
                - 'end_date' (pandas.Timestamp): Maximum `date_end` across
                                                 the day's observations.

    Notes:
        - `start_date` and `end_date` are derived from the full `df_day`
          DataFrame before the scene loop runs, not accumulated incrementally
          across scenes.
        - Scene pairs are deduplicated on `_unique_pair_key` (sensor names
          plus acquisition seconds for both scenes). When two scene_ids share
          a key, only the first encountered is processed and the duplicate is
          logged and skipped.
        - For level '00', a per-scene formatted CSV named
          `formatted_<scene_id>.csv` is written to `config['test_output_dir']`
          before outlier detection is applied.
        - `df_scenes` is assembled by concatenating each per-scene DataFrame
          after outlier detection. The caller produces daily-level outputs
          from this combined DataFrame rather than from per-scene files.
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
                config['test_output_dir'],
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
    Write day-level products for a single day from the combined per-scene
    DataFrame produced by `create_scene_output`.

    Depending on the processing level and the existence flags in `exists`,
    writes up to four product types: a multi-layered scenes NetCDF (one time
    layer per scene pair), a single-layer daily NetCDF, a GeoPackage, and a
    vector JSON file for the static web viewer. Each output is written only
    when its corresponding flag in `exists` is False.

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
                                                  detection; used as input to
                                                  `util.create_netcdf`,
                                                  `util.create_shape_package`,
                                                  and
                                                  `util.create_vector_json`.
        config (dict): Configuration dictionary. Must include:
                - 'file_server_3413' / 'file_server_6931' (str): Root output
                  path for the active EPSG. Daily data products are written
                  under `<file_server_<epsg>>/<data_files_dir>/<level_label>/
                  <year>/<type>/`.
                - 'viewer_dir' (str): Subdirectory under the file server
                  where vector JSON is written, in a `SIVelocity_SAR/`
                  folder.
                - 'level' (str): Processing level; controls which output
                  types are produced:
                      '00': NetCDF (scenes + daily), GeoPackage, vector JSON
                      '01': NetCDF (scenes + daily)
                      '02': NetCDF (scenes + daily), GeoPackage
                      '03': NetCDF (scenes + daily), GeoPackage, vector JSON
                - 'epsg' (int): EPSG code included in output filenames and
                                used to select the file server root.
                - 'version' (str): Version string included in output
                                   filenames.
        template_ds (xarray.Dataset): NetCDF template dataset passed directly
                                      to `util.create_netcdf`.
        exists (dict): Per-output existence flags from
            `_check_existing_files`. Keys `nc_scenes`, `nc_daily`, `gpkg`,
            and `json`; an output is written only when its flag is False.

    Returns:
        None

    Notes:
        - Output filenames follow the convention:
            `SIVelocity_SAR_<start>_<end>_<type>_12km_NH_<epsg>_
            PL<level>_v<version>.<ext>`
          where `<type>` is `scenes` for the multi-layered NetCDF and
          `daily` for the single-layer NetCDF and the GeoPackage.
        - Data product directories are created if they do not already exist,
          structured as `<file_server_<epsg>>/<data_files_dir>/<level_label>/
          <year>/<type>/`, where `<level_label>` is the short level label
          (e.g. 'PL03') and `<year>` is the four-digit start year.
        - Vector JSON is written to
          `<file_server_<epsg>>/<viewer_dir>/SIVelocity_SAR/` as
          `si_velocity_<start>.json`, accompanied by an `available_dates.json`
          index file.
        - All daily products are generated directly from
          `scene_output['df_scenes']` in a single pass.
    """

    import util
    import os
    import logging

    logger = logging.getLogger('sar_drift_converter')

    daily_start_date_str = scene_output['start_date'].strftime("%Y%m%d")
    daily_end_date_str = scene_output['end_date'].strftime("%Y%m%d")
    epsg = str(config['epsg'])
    lvl = f"PL{config['level']}"
    yr = str(daily_start_date_str[0:4])


    # multiple-layered netcdf
    if not exists['nc_scenes']:
        output_dir = os.path.join(
            config[f'file_server_{epsg}'], lvl, yr, 'nc'
        )
        os.makedirs(output_dir, exist_ok=True)
        # set Linux/Mac permissions on directory
        util._set_linux_permissions(output_dir, mode=0o775)
        
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
            config[f'file_server_{epsg}'], lvl, yr, 'nc'
        )
        os.makedirs(output_dir, exist_ok=True)
        # set Linux/Mac permissions on directory
        util._set_linux_permissions(output_dir, mode=0o775)
        
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
        output_dir = os.path.join(
            config[f'file_server_{epsg}'], lvl, yr, 'gpkg'
        )
        os.makedirs(output_dir, exist_ok=True)
        # set Linux/Mac permissions on directory
        util._set_linux_permissions(output_dir, mode=0o775)
        
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
        os.makedirs(config['json_dir'], exist_ok=True)
        # set Linux/Mac permissions on directory
        util._set_linux_permissions(config['json_dir'], mode=0o775)
               
        json_path = os.path.join(
            config['json_dir'],
            f"SIVelocity_SAR_{daily_start_date_str}_{daily_end_date_str}"
            f"_daily_12km_NH_{config['epsg']}_PL{config['level']}"
            f"_v{config['version']}.json"
        )
        available_dates_path = os.path.join(
            config['json_dir'],
            'available_dates.json'
        )
        
        util.create_vector_json(
            df=scene_output['df_scenes'],
            json_path=json_path,
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
    configured output files for each day. Called once per level/EPSG
    combination by `process_level_output`.

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

    Workflow:
        1. Validate `epsg` and `level` from config.
        2. Load the EPSG-specific CDL file as the NetCDF template dataset
           via `util._load_cdl_as_dataset`.
        3. Apply per-row and scene-level quality filters via
           `filter_input_data`.
        4. Construct a `_unique_pair_key` column (sensor names plus
           acquisition seconds for both scenes) used downstream to skip
           duplicate scene pairs.
        5. Assign a `date_range` column (YYYYMMDD of `date_start`).
        6. For each calendar day, call `_check_existing_files` to determine
           which outputs need to be written. Days within `reprocess_days`
           of today or where `overwrite` is True are always reprocessed;
           days where all outputs already exist are skipped.
        7. For each day requiring processing, call `create_scene_output`
           to run outlier detection and accumulate per-scene rows into
           `df_scenes`, then `create_daily_output` to write all daily
           products. A `gc.collect()` is issued after each day.
        8. For level '00', write raw and processing-codes CSVs per day to
           `config['test_output_dir']`.
        9. Log total elapsed run time for this level/EPSG on completion.

    Returns:
        None

    Notes:
        - Progress across days is displayed via a `tqdm` progress bar
          labelled with the active processing level and EPSG.
        - A `gc.collect()` call is made after each day to release memory
          held by per-scene DataFrames and outlier detection columns.
    """
    
    import util
    import os
    from datetime import datetime
    from tqdm import tqdm
    import logging
    import pandas as pd
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


    # load CDL file for NetCDF template
    template_ds = util._load_cdl_as_dataset(config)
    
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
    tqdm_desc = (
        f"Processing days (PL: {config['level']}; EPSG: {config['epsg']})..."
    )
    for day, df_day in tqdm(
            df_all.groupby('date_range'), tqdm_desc,
            unit=' day', unit_scale=False,
            colour='green'
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
            util.error_msg(f"Duplicate {key}")

                
        # combine all created daily files into one
        create_daily_output(scene_output, config, template_ds, exists)
        
        
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
                config['test_output_dir'],
                f"{daily_start_date_str}_{daily_end_date_str}_raw.csv"
            )
            df_day.to_csv(output_path, index=False)
            
            
            output_path = os.path.join(
                config['test_output_dir'],
                f"{daily_start_date_str}_{daily_end_date_str}_"
                "processing_codes.csv"
            )
            scene_output['df_scenes'].to_csv(output_path, index=False)


        # release the day's large objects before the next iteration
        scene_output['df_scenes'] = None
        del scene_output, df_day
        gc.collect()

        
    # final log entry
    run_end = datetime.utcnow() 
    elapsed = run_end - run_start
    logger.info(
        f"Run complete | {run_end} | elapsed={elapsed}"
    )
    
    
def process_level_output(test=False):
    """
    Top-level entry point for the SAR drift output generation pipeline.

    Parses and validates configuration, archives prior logs, refreshes the
    download directory, reads all input gfilter files into a single raw
    DataFrame, applies coordinate projections per target EPSG, then
    dispatches `create_level_output` for each level/EPSG combination.

    This function is intended to be called only when the script is run
    directly (`__name__ == "__main__"`).

    Workflow:
        1. Parse and validate runtime configuration via `read_json_config`.
        2. Compress any existing `.log` files in `config['log_dir']` to
           `.zip` archives, then initialise a fresh timestamped log file
           via `setup_logger`.
        3. Clear `config['sar_drift_download_directory']` of all files, then
           download recent gfilter files from `config['sar_drift_data_url']`
           via `util._download_sar_drift_files`.
        4. Gather candidate `.txt`/`.csv` files from both
           `sar_drift_download_directory` and `sar_drift_manual_directory`.
        5. Read all input files in parallel into a single raw DataFrame
           (`combine_into_dataframe`), drop duplicate rows, then drop any
           observation where polarization is not HH in both `File1` and
           `File2` (count logged).
        6. Apply EPSG-dependent coordinate projection once per target EPSG
           (`util._apply_projection`), producing one projected DataFrame
           per CRS. EPSGs processed: [3413, 6931].
        7. For each level/EPSG combination, call `create_level_output` with
           the pre-projected DataFrame for that EPSG. For levels '00' and
           '03', `start_date`/`end_date` bounds are written into config
           first.
        8. Log total elapsed run time on completion.

    Args:
        test (bool): If True, only processing level '00' is run instead of
            the production set ('01', '02', '03'), and a local
            `test_output/` directory is created for supplementary CSVs.
            Defaults to False.

    Notes:
        - Processing levels are hardcoded: ['01', '02', '03'] in production,
          ['00'] in test mode. They are not read from `config.json`.
        - EPSG codes are hardcoded as [3413, 6931]. File I/O runs only once;
          projection is applied per EPSG from the already-loaded DataFrame.
        - A cached EPSG:4326→EPSG:6931 transformer is stored on config for
          reuse during projection.
        - Previous log files are compressed to ZIP before the new log is
          created, preserving run history without accumulating uncompressed
          logs.
        - All level/EPSG combinations share one log file for the run; filter
          entries by level or EPSG to isolate a specific combination.
        - Pyproj CRS configuration is applied at startup via `pyproj_setup`.
        - On Windows, ProcessPoolExecutor uses the `spawn` start method, so
          this function must only be called from within an
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
    from pyproj import Transformer
    
    
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
    logger, log_path = setup_logger(config)
    logger.info(
        f"Process started | {run_start}"
    )


    # clear previously downloaded content
    downloaded_files = glob(
        os.path.join(config['sar_drift_download_directory'], '*')
    )
    for file in downloaded_files:
        os.remove(file)


    # download recent files
    util._download_sar_drift_files(config)
    
    
    # find files to process
    print("Gathering files to process (download and manual directories)...")
    files= []
    download_count = 0
    all_files = glob(os.path.join(config['sar_drift_download_directory'], '*'))
    for file in all_files:
        if ('.txt' in file) or ('.csv' in file):
            download_count += 1
            files.append(file)
            
    logger.info(f"Input directory: {config['sar_drift_download_directory']}")
    logger.info(f"Found {download_count} candidate files")            
        
    manual_count = 0
    all_files = glob(os.path.join(config['sar_drift_manual_directory'], '*'))
    for file in all_files:
        if ('.txt' in file) or ('.csv' in file):
            manual_count += 1
            files.append(file)
        
    logger.info(f"Input directory: {config['sar_drift_manual_directory']}")
    logger.info(f"Found {manual_count} candidate files")
    logger.info(f"Total candidate files {len(files)}")
    
    
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
        config['test_output_dir'] = 'test_output'
        if not os.path.exists(config['test_output_dir']):
            os.makedirs(config['test_output_dir'], exist_ok=True)
    else:
        processing_levels = ['01', '02', '03']
    
    obs_read=df_raw.shape[0]
    total_days=df_raw['date_start'].dt.date.nunique()
    total_scenes=len(np.unique(df_raw[['File1', 'File2']]))
    logger.info(
        f'Input data totals | total observations: {obs_read}; '
        f'total days: {total_days}; total scenes: {total_scenes}'
    )
    

    # cache transformer for better performance
    config['transformer_6931'] = Transformer.from_crs(
        "EPSG:4326", "EPSG:6931", always_xy=True
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
            create_level_output(df_by_epsg[epsg], config)



    # clean up downloaded files
    util._clear_download_dir(config)
    
    
    # final log entry
    run_end = datetime.utcnow() 
    elapsed = run_end - run_start
    logger.info(
        f"Process completed | {run_end} | elapsed={elapsed}"
    )
    
    
if __name__ == "__main__":
    process_level_output()
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
        - "sar_geotiff_filename"  (str):   Path to the SAR backscatter
                                           GeoTIFF image.
        - "netcdf_cdl_file"       (str):   Path to the base CDL file used for
                                           NetCDF metadata. The EPSG-specific
                                           variant is resolved at runtime by
                                           _set_metadata().
        - "netcdf_template_file"  (str):   Path to NetCDF template file on
                                           which scenes will be built.
        - "html_vector_template"  (str):   Path to HTML file that has the code
                                           to display vectors as interactive
                                           quivers with outliers                                            
        - "outlier_qml_file"      (str):   Path to QML file that applies
                                           outlier category styles to
                                           GeoPackages when opened in QGIS.
                                           Used for level '02'.
        - "graduated_qml_file"    (str):   Path to QML file that applies
                                           graduated vector styles to
                                           GeoPackages when opened in QGIS.
                                           Used for all levels other than '02'.
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
        "sar_drift_directory", "sar_drift_filename",
        "netcdf_cdl_file", "netcdf_template_file",
        "html_vector_template", "outlier_qml_file", "graduated_qml_file",
        "output_dir", "log_dir", "meta_dir", "file_server",
        "clear_output_dir", "batch_process", "overwrite", "delimiter",
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
        ('sar_drift_directory', 'sar_drift_directory', batch_process),
        ('sar_drift_filename', 'sar_drift_file', not batch_process),
        ('netcdf_cdl_file', 'netcdf_cdl_file', False),
        ('netcdf_template_file',  'netcdf_template_file', True),
        ('html_vector_template', 'html_vector_template', True),
        ('outlier_qml_file', 'outlier_qml_file', True),
        ('graduated_qml_file', 'graduated_qml_file', True),
        ('meta_dir', 'meta_dir', True),
        ('output_dir', 'output_dir', True),
        ('log_dir', 'log_dir', True),
        ('file_server', 'file_server', True)
    ]
    resolved_paths = {}
    for json_key, config_key, must_exist in path_checks:
        path = os.path.normpath(config[json_key])
        if must_exist and not os.path.exists(path):
            util.error_msg(f"Cannot find `{config_key}`: `{path}`")
        resolved_paths[config_key] = path

    # Delimiter decode (\t etc.)
    delimiter = config['delimiter'].encode().decode('unicode_escape')

    # Build final config — output_dir is set by create_level_output()
    config = {
        **resolved_paths,
        'clear_output_dir':        config['clear_output_dir'],
        'batch_process':           config['batch_process'],
        'overwrite':               config['overwrite'],
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
            'sar_drift_file':                'sar drift file',
            'netcdf_cdl_file':               'NetCDF CDL file',
            'netcdf_template_file':          'NetCDF template file',
            'html_vector_template':          'HTML vector template file',
            'outlier_qml_file':              'outlier qml file',
            'graduated_qml_file':            'graduated qml file',
            'meta_dir':                      'metadata directory',
            'output_dir':                    'output directory',
            'log_dir':                       'log directory',
            'file_server':                   'file server',
            'clear_output_dir':              'clear output directory',
            'batch_process':                 'batch process',
            'overwrite':                     'overwrite',
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

    import util
    import os
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
            executor.map(util._read_gfilter_file, args),
            total=len(args),
            desc='Reading gfilter files...'
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
    
        1. Remove rows where `direction_of_sea_ice_displacement == 0` or
           `sea_ice_speed == 0` (zero bearing or zero speed).
        2. Remove rows where `sea_ice_speed >= 25.0 m s⁻¹` (50 km files) or
           `>= 35.0 m s⁻¹` (75 km files).
        3. Remove rows where `Maxcorr2 <= Maxcorr1`.
    
        **Scene-level rejection (levels '02' and '03', entire scene
        discarded if):**
    
        1. Fewer than 60% of rows have `Maxcorr2 > Maxcorr1`, evaluated
           after the bearing/speed validity drop but before the per-row
           Maxcorr drop.
        2. Remaining row count falls below `ignore_vector_threshold` after
           all per-row drops.
    
        - Each filter step is logged individually, reporting rows dropped and
          the scene identifier. Rejected scenes are logged at WARNING level;
          accepted scenes and per-row drops at INFO level.
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
                mininterval=0
            ):
            scene_id = f"{file1}_{file2}"
            use_75km = df_scene['_use_75km'].iloc[0]
            initial_row_size = df_scene.shape[0]
    
            # remove invalid bearings and speeds
            df_scene = df_scene[
                (df_scene['direction_of_sea_ice_displacement'] != 0) &
                (df_scene['sea_ice_speed'] > 0)
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

    scene_i_j = {}
    scene_frames = []
    nc_files = []

    daily_start_date = pd.to_datetime(df_day['date_start'].min())
    daily_end_date   = pd.to_datetime(df_day['date_end'].max())

    scene_count = 0
    for scene_id, df_scene in df_day.groupby('scene_id'):
        scene_count += 1

        logger.info(
            f"Scene {scene_id} | "
            f"rows={len(df_scene)} | "
            f"date_range={day}"
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

        # only write NetCDF if it doesn't already exist
        if not exists['nc_scenes'] or not exists['nc_daily']:
            nc_path = util.create_netcdf(
                df=df_scene,
                base_name=scene_id,
                config=config,
                template_ds=template_ds,
                scene_i_j=scene_i_j
            )
            if nc_path:
                nc_files.append(nc_path)

    
    if scene_frames:
        df_scenes = pd.concat(scene_frames, ignore_index=True)
    else:
        df_scenes = pd.DataFrame()


    return {
        'scenes':     scene_count,
        'df_scenes':  df_scenes,
        'start_date': daily_start_date,
        'end_date':   daily_end_date,
        'nc_files':   nc_files,
    }
            
    
def create_daily_output(df_day, scene_output, config, template_ds, exists):
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
        df_day (pandas.DataFrame): All drift observations for the current day,
            as grouped upstream by `date_range`. Written to a raw formatted
            CSV unconditionally.
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
    import shutil
    import logging

    logger = logging.getLogger('sar_drift_converter')

    daily_start_date_str = scene_output['start_date'].strftime("%Y%m%d")
    daily_end_date_str = scene_output['end_date'].strftime("%Y%m%d")
    epsg = str(config['epsg'])
    lvl = f"Processing Level - {config['level']} (PL{config['level']})"
    yr = str(daily_start_date_str[0:4])


    # multiple-layered netcdf
    if not exists['nc_scenes']:
        output_dir = os.path.join(config['file_server'], epsg, lvl, yr, 'nc')
        os.makedirs(output_dir, exist_ok=True)
        scenes_nc_path = os.path.join(
            output_dir,
            f"SIVelocity_SAR_{daily_start_date_str}_{daily_end_date_str}"
            f"_scenes_12km_NH_{config['epsg']}_PL{config['level']}"
            f"_v{config['version']}.nc"
        )
        util.combine_daily_netcdf_files(
            config=config,
            nc_files=scene_output['nc_files'],
            template_ds=template_ds,
            daily_start_date=scene_output['start_date'],
            daily_end_date=scene_output['end_date'],
            daily_nc_path=scenes_nc_path
        )


    # single-layer netcdf
    if not exists['nc_daily']:
        daily_nc_path = os.path.join(
            output_dir,
            f"SIVelocity_SAR_{daily_start_date_str}_{daily_end_date_str}"
            f"_daily_12km_NH_{config['epsg']}_PL{config['level']}"
            f"_v{config['version']}.nc"
        )
        util.combine_daily_netcdf_files(
            config=config,
            nc_files=scene_output['nc_files'],
            template_ds=template_ds,
            daily_start_date=scene_output['start_date'],
            daily_end_date=scene_output['end_date'],
            daily_nc_path=daily_nc_path,
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
            config['html_vector_template']
        )
                
        json_path = os.path.join(
            data_dir, f"si_velocity_{daily_start_date_str}.json"
        )
        available_dates_path = os.path.join(
            data_dir, 'available_dates.json'
        )
        
        util.create_vector_html_and_json(
            df=scene_output['df_scenes'],
            html_path=html_path,
            data_dir=data_dir,
            json_path=json_path,
            available_dates_path=available_dates_path,
            config=config
        )


    if config['level'] == '00':
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


    logger.info(
        f"Day {daily_start_date_str}_{daily_end_date_str} complete | "
        f"scenes={scene_output['scenes']}"
    )


def create_level_output(df_all, level, epsg, config):
    """
    Main execution workflow for converting SAR drift text files into
    GeoPackage, NetCDF, and Plotly HTML outputs.

    Args:
        level  (str):  Processing level; controls filtering and output files
                       created. Must be one of: '00', '01', '02', or '03'.
        epsg   (int):  Output projection EPSG code. Must be 3413 (NSIDC polar
                       stereographic north) or 6931 (NSIDC ease-grid 2.0
                       north).
        config (dict): Validated configuration dictionary returned by
                       `read_json_config()`. `level` and `epsg` are written
                       into this dict at the start of execution.

    Workflow:
        1. Validate `level` and `epsg` and assign them into `config`.
        2. Set up the output directory tree under
           `level_output/<level>/` and optionally clear it if
           `config['clear_output_dir']` is True.
        3. Open the NetCDF template specified by
           `config['netcdf_template_file']` to provide the target grid.
        4. Glob-match input `.txt` and `.csv` files from
           `config['sar_drift_directory']` (batch mode) or load a single
           file from `config['sar_drift_file']` (single-file mode),
           controlled by `config['batch_process']`.
        5. Read and combine all matched input files into a single DataFrame
           via `combine_into_dataframe()`.
        6. Apply per-row and scene-level quality filters via
           `filter_input_data()`.
        7. Assign a `date_range` column (YYYYMMDD of `date_start`) and log
           any observations that span more than one calendar day.
        8. Group observations by `date_range`, then for each day call
           `create_scene_output()` to produce per-scene outputs, followed
           by `create_daily_output()` to combine scenes into daily files.
        9. Log total elapsed run time on completion.

    Configuration keys used:
        - 'batch_process'      (bool): If True, process all `.txt`/`.csv`
                                       files in `sar_drift_directory`;
                                       if False, process `sar_drift_file`
                                       only.
        - 'clear_output_dir'   (bool): If True, delete and recreate the
                                       output directory before processing.
        - 'sar_drift_directory' (str): Input directory for batch processing.
        - 'sar_drift_file'      (str): Path to a single input file.
        - 'netcdf_template_file'(str): Path to the NSIDC NetCDF template
                                       providing the target grid.
        - 'output_dir'          (str): Set internally to
                                       `level_output/<level>/`; used as the
                                       root for all output subdirectories.

    Notes:
        - Progress across days is displayed via a `tqdm` progress bar.
        - Observations where `date_end` falls on a different calendar day
          than `date_start` are logged individually by scene with their
          maximum time span.
    """
    
    import util
    import os
    import shutil
    from datetime import datetime
    from glob import glob
    from tqdm import tqdm
    import logging
    import pandas as pd
    import xarray as xr

    
    run_start = datetime.utcnow()


    # epsg validation
    if epsg not in [3413, 6931]:
        util.error_msg('`epsg` must be `3413` or `6931`')
    else:
        config['epsg'] = epsg
        
    # level validation
    if level not in ['00', '01', '02', '03']:
        util.error_msg('`level` must be one of: `00`, `01`, `02`, `03`')
    else:
        config['level'] = level
    


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
    df_all = filter_input_data(df_all, config)

    
    # create date range groups for daily/scene output
    print('Creating groups based on start day...')
    df_all['date_range'] = (
        pd.to_datetime(df_all['date_start']).dt.strftime('%Y%m%d')
    )
    
    
    ####################################################
    # NEEDED TO DEBUG BUT NOT NECESSARY TO LOG ANYMORE #
    ####################################################
    # # log rows that span more than one calendar day
    # multi_day = (
    #     pd.to_datetime(df_all['date_end']).dt.strftime('%Y%m%d') !=
    #     df_all['date_range']
    # )
    # if multi_day.any():
    #     multi_count = multi_day.sum()
    #     logger.info(
    #         f"{multi_count} observations span more than one calendar day"
    #     )
    #     # log per scene
    #     for scene_id, grp in df_all[multi_day].groupby('scene_id'):
    #         max_span = (
    #             pd.to_datetime(grp['date_end']).max() -
    #             pd.to_datetime(grp['date_start']).min()
    #         )
    #         if max_span > pd.Timedelta(days=1):
    #             logger.info(
    #                 f"Multi-day scene: {scene_id} | "
    #                 f"rows={grp.shape[0]} | max_span={max_span}"
    #             )
    
   
    # create output: group by day, then by scene within each day
    start_days = {}
    for day, df_day in tqdm(
            df_all.groupby('date_range'), "Processing days..."
        ):        
        
        logger.info(f"Processing day: {day}")
        
        stub = {
            'start_date': pd.to_datetime(df_day['date_start']).min(),
            'end_date':   pd.to_datetime(df_day['date_end']).max(),
        }

        exists = util._check_existing_files(stub, config)
        
        

        # if all(exists.values()):
        #     logger.info(
        #         f"Skipping {stub['start_date'].strftime('%Y%m%d')}. "
        #         f"All level {config['level']} outputs already exist"
        #     )
        #     continue

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
        create_daily_output(df_day, scene_output, config, template_ds, exists)            
    

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
    df_raw = combine_into_dataframe(files, config)

    espg_list = [3413, 6931]
    if test:
        processing_levels = ['00']
    else:
        processing_levels = ['01', '02', '03']
    
    obs_read=df_raw.shape[0]
    total_days=df_raw['date_start'].dt.date.nunique()
    total_scenes=len(df_raw[['File1', 'File2']].drop_duplicates())
    logger.info(
        f'Input data totals | total observations: {obs_read}; '
        f'total days: {total_days}; total scenes: {total_scenes}'
    )
    
    df_by_epsg = {}
    for epsg in espg_list:
        df_by_epsg[epsg] = util._apply_projection(df_raw, epsg, config)
    
    for level in processing_levels:
        for epsg in espg_list:
            config['level'] = level
            config['epsg'] = epsg
            create_level_output(df_by_epsg[epsg], level, epsg, config)


    # final log entry
    run_end = datetime.utcnow() 
    elapsed = run_end - run_start
    logger.info(
        f"Process completed | {run_end} | elapsed={elapsed}"
    )
    
    
if __name__ == "__main__":
    process_level_output()
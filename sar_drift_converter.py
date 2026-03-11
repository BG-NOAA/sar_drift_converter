# -*- coding: utf-8 -*-
"""
******************************************************************************

 Project:    SAR Drift Output Generator
 Purpose:    Create shape file package (.gpkg) and NetCDF file (.nc) from the
             SAR drift daily file. This script allows the data to be visualized
             in QGIS or any program that can read NetCDF
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


def read_json_config():
    """
    Parse and validate configuration for SAR Drift Output Generator.
    
    This function reads a JSON config file specified via the `-c` or 
    `--config_file` argument and validates its contents against a strict
    schema. It ensures all required inputs (SAR drift file, GeoTIFF, 
    CDL metadata, output directory) exist and validates types and formatting
    for each parameter.
    
    Expected JSON keys (must match exactly):
        - "sar_drift_directory"    (str):   Path to directory containing
                                            multiple SAR drift delimited files
                                            for batch processing.
        - "sar_drift_filename"     (str):   Path to a single SAR drift
                                            delimited text file.
        - "sar_geotiff_filename"   (str):   Path to the SAR backscatter
                                            GeoTIFF image.
        - "netcdf_cdl_file"        (str):   Path to the CDL file used for
                                            NetCDF metadata.
        - "netcdf_template_file"   (str):   Path to NetCDF template file on
                                            which scenes will be built.
        - "qml_file"               (str):   Path to QML file that applies a
                                            style to GeoPackages when opened
                                            in QGIS.
        - "output_dir"             (str):   Output directory where generated
                                            files will be stored.
        - "clear_output_dir"       (bool):  Remove output directory and all
                                            contents from previous runs.
        - "batch_process"          (bool):  If True, process all files in
                                            `sar_drift_directory`; if False,
                                            process single `sar_drift_filename`.
        - "delimiter"              (str):   Field separator in the input file
                                            (e.g., ",", "\\t").
        - "skip_rows_before_header"(int):   Number of rows to skip before
                                            the header in the data file.
        - "ignore_vector_threshold"(int):   Ignore data files where the number
                                            of vector observations falls below
                                            this threshold.
        - "z_score_level"          (float): Z-score threshold for distance and
                                            bearing outlier detection.
        - "chi_square_level"       (float): Chi-square tail probability for
                                            Mahalanobis distance thresholding.
        - "neighbor_radius_km"     (float): Neighbor search radius in
                                            kilometers.
        - "min_neighbors"          (int):   Minimum neighbors required to mark
                                            a z-score result as statistically
                                            confident.
        - "md_min_neighbors"       (int):   Minimum neighbors required to mark
                                            a Mahalanobis distance result as
                                            statistically confident.
        - "outlier_passes"         (int):   Number of iterative passes to
                                            remove outliers from the neighbor
                                            pool and recompute.
        - "use_geotiff"            (bool):  Use a supplied GeoTIFF file as
                                            background for output images.
        - "create_region_plot"     (bool):  If True, create a map of the
                                            observed region with vectors
                                            overlaid on the GeoTIFF; if False,
                                            render vectors only.
        - "vector_stride"          (int):   Display every nth vector (1 = all
                                            vectors).
        - "inlier_vector_stride"   (int):   Display every nth vector for the
                                            inliers-only plot (1 = all).
        - "quiver_scale_small_area"(float): Quiver arrow scale for small area
                                            plots.
        - "quiver_scale_large_area"(float): Quiver arrow scale for large area
                                            plots.
        - "precision"              (int):   Number of decimal places to retain
                                            in outputs.
        - "verbose"                (bool):  Print detailed parameter info to
                                            the console.
        - "version"                (str):   Processing version; controls
                                            filtering level and output files
                                            created. Must be one of:
                                            '00', '01', '02', or '03'.

    Command-line arguments:
        -c, --config_file: Path to a JSON file with all required configuration.

    Returns:
        dict: Validated configuration dictionary with normalized paths and
              resolved output subdirectories:
              - 'formatted_data_dir': <output_dir>/formatted_data
              - 'gpkg_dir':           <output_dir>/gpkg
              - 'nc_dir':             <output_dir>/nc
              - 'png_dir':            <output_dir>/png

    Raises:
        Exits the script (status code 1) if:
            - Config file is missing or improperly formatted.
            - Required files or directories do not exist.
            - Parameter types are invalid (e.g., non-integer precision).
            - Unexpected or missing keys are present in the JSON.
            - Numeric parameters are out of valid range.
            - Version is not one of '00', '01', '02', or '03'.

    Example:
        $ python sar_drift_output.py -c config.json
    """

    import util
    import argparse
    import os
    import shutil
    import json


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


    # Key validation
    required_json_keys = {
        "sar_drift_directory", "sar_drift_filename", "sar_geotiff_filename",
        "netcdf_cdl_file", "netcdf_template_file", "qml_file", "output_dir",
        "clear_output_dir", "batch_process", "delimiter",
        "skip_rows_before_header", "ignore_vector_threshold", "z_score_level",
        "chi_square_level", "neighbor_radius_km", "min_neighbors",
        "md_min_neighbors", "outlier_passes", "use_geotiff",
        "create_region_plot", "vector_stride", "inlier_vector_stride",
        "quiver_scale_small_area", "quiver_scale_large_area", "precision",
        "verbose", "version"
    }
    config_keys = set(config.keys())
    missing = required_json_keys - config_keys
    extra   = config_keys - required_json_keys
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
        ("batch_process",             bool,  None, None),
        ("clear_output_dir",          bool,  None, None),
        ("use_geotiff",               bool,  None, None),
        ("create_region_plot",        bool,  None, None),
        ("verbose",                   bool,  None, None),
        ("skip_rows_before_header",   int,   0,    True),
        ("ignore_vector_threshold",   int,   1,    False),
        ("min_neighbors",             int,   0,    True),
        ("md_min_neighbors",          int,   0,    True),
        ("outlier_passes",            int,   0,    True),
        ("vector_stride",             int,   1,    False),
        ("inlier_vector_stride",      int,   1,    False),
        ("precision",                 int,   0,    True),
        ("z_score_level",             float, 0.0,  False),
        ("chi_square_level",          float, 0.0,  False),
        ("neighbor_radius_km",        float, 0.0,  False),
        ("quiver_scale_small_area",   float, None, None),
        ("quiver_scale_large_area",   float, None, None),
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


    # Version validation
    if config['version'] not in ['00', '01', '02', '03']:
        util.error_msg('`version` must be one of: `00`, `01`, `02`, `03`')


    # Path resolution and existence checks
    batch_process = config['batch_process']
    path_checks = [
        ('sar_drift_directory', 'sar_drift_directory', batch_process),
        ('sar_drift_filename', 'sar_drift_file', not batch_process),
        ('sar_geotiff_filename', 'sar_geotiff_file', config['use_geotiff']),
        ('netcdf_cdl_file', 'netcdf_cdl_file', True),
        ('netcdf_template_file', 'netcdf_template_file', True),
        ('qml_file', 'qml_file', True)
    ]
    resolved_paths = {}
    for json_key, config_key, must_exist in path_checks:
        path = os.path.normpath(config[json_key])
        if must_exist and not os.path.exists(path):
            util.error_msg(f"Cannot find `{config_key}`: `{path}`")
        resolved_paths[config_key] = path

    
    # Output directory setup
    output_dir = os.path.normpath(config['output_dir'])
    if os.path.exists(output_dir) and config['clear_output_dir']:
        shutil.rmtree(output_dir)

    subdirs = ['formatted_data', 'gpkg', 'nc', 'png']
    subdir_paths = {}
    for name in subdirs:
        path = os.path.join(output_dir, name)
        os.makedirs(path, exist_ok=True)
        subdir_paths[f'{name}_dir'] = path

    
    # Delimiter decode (\t etc.)
        delimiter = config['delimiter'].encode().decode('unicode_escape')

    
    # Build final config
    config = {
        **resolved_paths,
        'output_dir':              output_dir,
        **subdir_paths,
        'clear_output_dir':        config['clear_output_dir'],
        'batch_process':           config['batch_process'],
        'delimiter':               delimiter,
        'skip_rows_before_header': config['skip_rows_before_header'],
        'ignore_vector_threshold': config['ignore_vector_threshold'],
        'z_score_level':           config['z_score_level'],
        'chi_square_level':        config['chi_square_level'],
        'neighbor_radius_km':      config['neighbor_radius_km'],
        'min_neighbors':           config['min_neighbors'],
        'md_min_neighbors':        config['md_min_neighbors'],
        'outlier_passes':          config['outlier_passes'],
        'use_geotiff':             config['use_geotiff'],
        'create_region_plot':      config['create_region_plot'],
        'vector_stride':           config['vector_stride'],
        'inlier_vector_stride':    config['inlier_vector_stride'],
        'quiver_scale_small_area': config['quiver_scale_small_area'],
        'quiver_scale_large_area': config['quiver_scale_large_area'],
        'precision':               config['precision'],
        'verbose':                 config['verbose'],
        'version':                 config['version'],
    }

    
    # echo
    if config['verbose']:
        labels = {
            'sar_drift_directory':    'sar drift directory',
            'sar_drift_file':         'sar drift file',
            'sar_geotiff_file':       'sar geotiff file',
            'netcdf_cdl_file':        'NetCDF CDL file',
            'netcdf_template_file':   'NetCDF template file',
            'qml_file':               'qml file',
            'output_dir':             'output directory',
            'batch_process':          'batch process',
            'clear_output_dir':       'clear output dir',
            'delimiter':              'delimiter',
            'skip_rows_before_header':'skip rows before header',
            'ignore_vector_threshold':'ignore vector threshold',
            'z_score_level':          'z-score level',
            'chi_square_level':       'chi-square level',
            'neighbor_radius_km':     'neighbor radius (km)',
            'min_neighbors':          'minimum neighbors',
            'md_min_neighbors':       'MD minimum neighbors',
            'outlier_passes':         'outlier passes',
            'use_geotiff':            'use geotiff image',
            'create_region_plot':     'create region plot',
            'vector_stride':          'vector stride',
            'inlier_vector_stride':   'inlier vector stride',
            'quiver_scale_small_area':'quiver scale small area',
            'quiver_scale_large_area':'quiver scale large area',
            'precision':              'precision',
            'version':                'version',
        }
        lines = ["CONF PARAMS:"]
        for key, label in labels.items():
            val = f"`{config[key]}`" if key == 'delimiter' else config[key]
            lines.append(f"  {label:<25} {val}")
        print('\n'.join(lines))

    return config


def main():
    """
    Main execution workflow for converting SAR drift data to GeoPackage
    and NetCDF formats.

    This function:
    - Parses command-line arguments
    - Loads and preprocesses the SAR drift input file
    - Generates a GeoPackage file containing point and line geometries for QGIS
    - Generates a CF-compliant NetCDF file using metadata from a CDL template

    The output files are saved to the specified output directory.

    This function is intended to be executed when the script is run
    as a standalone program.
    """

    # import sar_drift as sd
    import util
    import os
    from glob import glob
    from tqdm import tqdm
    import pandas as pd
    import xarray as xr
    
    # parse user arguments
    config = read_json_config()
    
    # load NSIDC polar stereographic EPSG:3411 NetCDF template
    with xr.open_dataset(config['netcdf_template_file']) as ds:
        template_ds = ds.load()


    # find files to process
    files= []
    if config['batch_process']:
        all_files = glob(os.path.join(config['sar_drift_directory'], '*'))
        for file in all_files:
            if ('.txt' in file) or ('.csv' in file):
                files.append(file)
    else:
        files = [config['sar_drift_file']]
        
    
    updated_files = []
    for gfilter_path in files:
        
        basename, ext = os.path.splitext(gfilter_path)
        if '_' in ext:
            ext = ext.split('_')[0]
        normalized_gfilter_path = basename + ext
            
        
        """
        Use 0075000m file instead of 0050000m.
        Check as normalized .txt file name since 007500m doesn't have
        _counter after .txt extension
        """
        gfilter_path_75km = normalized_gfilter_path.replace(
            '_0050000m_',
            '_0075000m_',
        )
        
        
        if os.path.exists(gfilter_path_75km):
            updated_files.append(gfilter_path_75km)
        else:
            # use original file name with counter after .txt_
            updated_files.append(gfilter_path)

        
        if int(config['version']) > 1:
            # get high-level content of data file
            # Read SAR drift data file
            df = util.read_sar_drift_data_file(
                input_file=updated_files[-1], #file just appeneded
                config=config
            )
            if df.shape[0] < config['ignore_vector_threshold']:
                # ignore files with few observations
                updated_files.pop()
                continue
        
            
            # skip 75km file if MaxCorr2 > MaxCorr1 for < 60% of the data
            if '_0075000m_' in gfilter_path:
                pct_correct = (df['Maxcorr2'] > df['Maxcorr1']).mean() * 100
                if pct_correct < 60:
                    print(
                        "Reject file: "
                        f"{os.path.basename(updated_files[-1])}\n"
                        f"pct_correct={pct_correct:.1f}% (<60%)"
                    )
                    updated_files.pop()
    
    
    scene_i_j = {}
    daily_start_date, daily_end_date = None, None
    for data_file in tqdm(updated_files, desc='Processing data files...'):

        # set base name for output files
        data_file_basename = os.path.splitext(
            os.path.basename(data_file)
        )[0]
    
           
        # Read SAR drift data file
        df_sar = util.read_sar_drift_data_file(
            input_file=data_file,
            config=config
        )
    
        output_path = os.path.join(
            config['formatted_data_dir'],
            f"formatted_{data_file_basename}.csv"
        )
        df_sar.to_csv(output_path, index=False)
        
        
    
        """
        Per OSI SAF, the dates in file names that have motion data
        the dates in the file typically is the end date of the observation
        period https://osisaf-hl.met.no/sites/osisaf-hl/files/user_manuals/
        osisaf_pum_sea-ice-drift-lr_v1p9.pdf
        (Page 25)
        
        Version `0` indicates first process wihtout cleaned data
        
        For multiple pairs in one period, have included start/end date/time
        """
        start_min = pd.to_datetime(df_sar['Date1'].min())
        if daily_start_date is None or start_min < daily_start_date:
            daily_start_date = start_min

        end_max = pd.to_datetime(df_sar['Date2'].max())
        if daily_end_date is None or end_max > daily_end_date:
            daily_end_date = end_max
    
        # continue # get right to concatenating

        # Detect outliers (will return all 00 if not active)
        df_sar = util.outlier_search(
            df=df_sar,
            config=config,
            base_name=data_file_basename,
            radius_km=config['neighbor_radius_km'],
            min_neighbors=config['min_neighbors'],
            md_neighbors=config['md_min_neighbors'],
            z_score_level=config['z_score_level'],
            chi_square_level=config['chi_square_level'],
            passes=config['outlier_passes'] 
        )

        
        # Create NetCDF always
        util.create_netcdf(
            df=df_sar,
            base_name=data_file_basename,
            config=config,
            template_ds=template_ds,
            scene_i_j=scene_i_j
        )


        if int(config['version']) > 1 or config['version'] == '00':
            # Create shape file package for QGIS    
            util.create_shape_package(
                df=df_sar,
                base_name=data_file_basename,
                config=config
            )


        if int(config['version']) > 2 or config['version'] == '00':
            # create individual PNG file from NetCDF
            util.create_png(
                config=config,
                base_name=data_file_basename
            )

    
        # Overlay SAR drift data vectors on geotiff image
        # util.overlay_sar_drift_on_geotiff(
        #     config=config,
        #     gdf_lines=gdf_lines,
        #     df_sar=df_sar,
        #     base_name=data_file_basename
        # )
        

    """
    read through each scene_i_j dictionary items
    ((i, j) coordinates in each scene)
    Get the counts of each (i, j) coordinate found in the entire set of scenes
    per time period
    Show the count of each (i, j) coordinate and the scenes where they exist
    """
    df = pd.DataFrame(columns=['scene', 'item_count', 'items'])
    for idx, (scene, coords) in enumerate(scene_i_j.items()):
        df.loc[idx] = [scene, len(coords), coords]
    df = df.sort_values('item_count', ascending=True)
    df.to_csv(r'output/scenes.csv')

    
    from collections import Counter, defaultdict
    cell_counts = Counter()
    cell_scenes = defaultdict(list)
    
    for scene, items in zip(df['scene'], df['items']):
        uniq_cells = set(items)
        cell_counts.update(uniq_cells)
        for cell in uniq_cells:
            cell_scenes[cell].append(scene)
    df_report = pd.DataFrame(columns=['Cell', 'Count', 'Scenes'])
    for idx, (i_j, count) in enumerate(cell_counts.most_common(50)):
        df_report.loc[idx] = [i_j, count, cell_scenes[i_j]]
    df_report.to_csv(r'output/scene_report.csv', index=False)

        
    
    # combine all created netcdf files into one
    nc_files = glob(os.path.join(config["output_dir"], 'nc', '*.nc'))
    daily_start_date_str = daily_start_date.strftime("%Y%m%d")
    daily_end_date_str = daily_end_date.strftime("%Y%m%d")
    
    # multiple layers
    daily_nc_path = os.path.join(
        config["output_dir"],
        f"SIVelocity_SAR_{daily_start_date_str}_{daily_end_date_str}"
        f"_scenes_12km_NH_v{config['version']}.nc"
    )
    util.combine_daily_netcdf_files(
        config=config,
        nc_files=nc_files,
        template_ds=template_ds,
        daily_start_date=daily_start_date,
        daily_end_date=daily_end_date,
        daily_nc_path=daily_nc_path
    )
    
    
    # one layer
    daily_nc_path = os.path.join(
        config["output_dir"],
        f"SIVelocity_SAR_{daily_start_date_str}_{daily_end_date_str}"
        f"_daily_12km_NH_v{config['version']}.nc"
    )
    util.combine_daily_netcdf_files(
        config=config,
        nc_files=nc_files,
        template_ds=template_ds,
        daily_start_date=daily_start_date,
        daily_end_date=daily_end_date,
        daily_nc_path=daily_nc_path,
        multi_layered=False
    )
    
    
if __name__ == "__main__":
    main()
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
        - "sar_drift_directory (str): Path to where process multiple SAR
                                      drift delimited files.
        - "sar_drift_filename" (str): Path to the SAR drift delimited
                                      text file.
        - "sar_geotiff_filename" (str): Path to the SAR backscatter GeoTIFF
                                        image.
        - "netcdf_cdl_file" (str): Path to the CDL file used for
                                   NetCDF metadata.
        - "output_dir" (str): Output directory where generated files will
                              be stored.
        - "batch_process" (bool): Process one file `sar_drift_filename` or
                                  multiple files `sar_drift_directory`.
        - "delimiter" (str): Field separator in the input file
                             (e.g., ",", "\t").
        - "skip_rows_before_header" (int): Number of rows to skip before header
                                           in data file.
        - "detect_outliers" (bool): Look for outliers when process input data.
        - "ignore_vector_threshold" (int): Ignore data files if the number of
                                           vector observations are below the
                                           threshold
        - "use_geotiff" (bool): Use a supplied geotiff file as background for
                                output images
        - "create_region_plot" (bool): If True, create a map of the observed
                                       region along with the vectors on top of
                                       the geotiff image. If False, just create
                                       the vectors on top of the geotiff image.
        - "vector_stride" (int): Display every vector (1) or use a step
                                 to display every nth vector
        - "inlier_vector_stride" (int): Display every vector (1) or use a step
                                        to display every nth vector for the all
                                        inliers plot.
        - "quiver_scale_small_area" (int): Size of the quiver for small area
                                           plots.
        - "quiver_scale_large_area" (int): Size of the quiver for large area
                                           plots.
        - "precision" (int): Number of decimal places to retain in outputs.
        - "verbose" (bool): Print detailed parameter info to the console.
    
    Command-line arguments:
        -c, --config_file: Path to a JSON file with all required configuration.
    
    Returns:
        dict: A dictionary of JSON keys and their values
    
    Raises:
        Exits the script (status code 1–19) if:
            - Config file is missing or improperly formatted.
            - Required files or directories do not exist.
            - Types for fields like `precision` or `verbose` are invalid.
            - Unexpected or missing keys are present in the JSON.
    
    Example:
        $ python sar_drift_output.py -c config.json
    """

    import util
    import argparse
    import os
    import json


    # json config file
    parser = argparse.ArgumentParser(
        description='Converts SAR drift data to .gpkg and .nc files.'
        )
    
    parser.add_argument(
        '-c', '--config_file',
        type=str,
        action='store',
        help='Path to config JSON file'
        )

    args = parser.parse_args()
    if not args.config_file:
        util.error_msg('Missing or empty config file argument', 1)
        
    
    config_file = os.path.normpath(os.path.join(args.config_file))
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    # confirm the needed keys, and only those keys, exist
    required_json_keys = {
        "sar_drift_directory",
        "sar_drift_filename",
        "sar_geotiff_filename",
        "netcdf_cdl_file",
        "output_dir",
        "batch_process",
        "delimiter",
        "skip_rows_before_header",
        "detect_outliers",
        "ignore_vector_threshold",
        "use_geotiff",
        "create_region_plot",
        "vector_stride",
        "inlier_vector_stride",
        "quiver_scale_small_area",
        "quiver_scale_large_area",
        "precision",
        "verbose"
    }        
    config_keys = set(config.keys())
    if config_keys != required_json_keys:
        missing = required_json_keys - config_keys
        extra = config_keys - required_json_keys
        if missing:
            util.error_msg(
                f"Missing required keys in {config_file}: "
                f"{', '.join(missing)}",
                2
            )
        if extra:
            util.error_msg(
                f"Unexpected keys in {config_file}: {', '.join(extra)}",
                3
            )

    # check sar drift directory exists
    batch_process = config['batch_process']
    if not isinstance(batch_process, bool):
        util.error_msg(
            f'`batch_process` must be boolen, '
            f'got {type(batch_process).__name__}',
            4
        )
    batch_process = bool(batch_process)
    sar_drift_directory = os.path.normpath(
        os.path.join(config['sar_drift_directory'])
    )
    if not os.path.exists(sar_drift_directory) and batch_process:
        util.error_msg(
            f"Cannot find sar_drift_directory `{sar_drift_directory}`",
            5
        )
        
        
    # check sar drift file exists
    sar_drift_file = os.path.normpath(
        os.path.join(config['sar_drift_filename'])
    )
    if not os.path.exists(sar_drift_file) and not batch_process:
        util.error_msg(f"Cannot find sar_drift_file `{sar_drift_file}`", 6)
        

    # check sar geotiff file exists
    use_geotiff = config['use_geotiff']
    if not isinstance(use_geotiff, bool):
        util.error_msg(
            f'`use_geotiff` must be boolen, '
            f'got {type(use_geotiff).__name__}',
            7
        )
    use_geotiff = bool(use_geotiff)
    sar_geotiff_file = os.path.normpath(
        os.path.join(config['sar_geotiff_filename'])
    )
    if not os.path.exists(sar_geotiff_file) and use_geotiff:
        util.error_msg(
            f"Cannot find sar_getotiff_file `{sar_geotiff_file}`\n\t"
            f"---`use_geotiff` in {config_file} set to "
            f"`{config['use_geotiff']}`---",
            8
        )


    # check netcdf cdl file exists
    netcdf_cdl_file = os.path.normpath(
        os.path.join(config['netcdf_cdl_file']
    ))
    if not os.path.exists(netcdf_cdl_file):
        util.error_msg(
            f"Cannot find NetCDF CDL file `{netcdf_cdl_file}`",
            9
        )
        
        
    # check output dir exists
    output_dir = os.path.normpath(os.path.join(config['output_dir']))
    if not os.path.exists(output_dir):
        util.error_msg(
            f"Cannot find output directory `{output_dir}`",
            10
        )
    else:
        # create subfolders
        formatted_data_dir = os.path.join(output_dir, 'formatted_data')
        os.makedirs(formatted_data_dir, exist_ok=True)
        gpkg_dir = os.path.join(output_dir, 'gpkg')
        os.makedirs(gpkg_dir, exist_ok=True)
        nc_dir = os.path.join(output_dir, 'nc')
        os.makedirs(nc_dir, exist_ok=True)
        png_dir = os.path.join(output_dir, 'png')
        os.makedirs(png_dir, exist_ok=True)


    # delimiter character (encode().decode handles \t)
    delimiter = config['delimiter'].encode().decode('unicode_escape')
    
    
    # header rows to skip
    skip_rows_before_header = config['skip_rows_before_header']
    if not isinstance(skip_rows_before_header, int):
        util.error_msg(
            f'`skip_header_rows` must be an integer, '
            f'got {type(skip_rows_before_header).__name__}',
            11
        )
    skip_rows_before_header = int(skip_rows_before_header)
    if skip_rows_before_header < 0:
        util.error_msg(
            f'`skip_header_rwos = {skip_rows_before_header} `'
            ' cannot be negative.',
            12
        )
    
            
    # detect outlier when process input files   
    detect_outliers = config['detect_outliers']
    if not isinstance(detect_outliers, bool):
        util.error_msg(
            f'`detect_outliers` must be boolen, '
            f'got {type(detect_outliers).__name__}',
            13
        )
    detect_outliers = bool(detect_outliers)
    

    # ignore data files where vector observations are below the threshold
    ignore_vector_threshold = config['ignore_vector_threshold']
    if not isinstance(ignore_vector_threshold, int):
        util.error_msg(
            f'`ignore_vector_threshold` must be an integer, '
            f'got {type(ignore_vector_threshold).__name__}',
            14
        )
    ignore_vector_threshold = int(ignore_vector_threshold)
    if ignore_vector_threshold < 1:
        util.error_msg(
            f'`ignore_vector_threshold = {ignore_vector_threshold} `'
            ' must be greater than 1.',
            15
        )
        
    # create subplots with region or just vectors on geotiff image
    create_region_plot = config['create_region_plot']
    if not isinstance(create_region_plot, bool):
        util.error_msg(
            f'`create_region_plot` must be boolen, '
            f'got {type(create_region_plot).__name__}',
            16
        )
    create_region_plot = bool(create_region_plot)
    
    
    # vector stride (offset count of records in SAR drift data)
    vector_stride = config['vector_stride']
    if not isinstance(vector_stride, int):
        util.error_msg(
            f'`vector_stride` must be an integer, '
            f'got {type(vector_stride).__name__}',
            17
        )
    vector_stride = int(vector_stride)
    if vector_stride < 1:
        util.error_msg(
            f'`vector_stride = {vector_stride} ` must be greater than 1.',
            18
        )


    # inlier vector stride (offset count for vectors in all inliers plot)
    inlier_vector_stride = config['inlier_vector_stride']
    if not isinstance(inlier_vector_stride, int):
        util.error_msg(
            f'`inlier_vector_stride` must be an integer, '
            f'got {type(inlier_vector_stride).__name__}',
            19
        )
    vector_stride = int(vector_stride)
    if vector_stride < 1:
        util.error_msg(
            f'`vector_stride = {vector_stride} ` must be greater than 1.',
            20
        )
        
    # quiver scale (relational size of arrows in plot)
    quiver_scale_small_area = config['quiver_scale_small_area']
    if not isinstance(quiver_scale_small_area, float):
        util.error_msg(
            f'`quiver_scale_small_area` must be a float, '
            f'got {type(quiver_scale_small_area).__name__}',
            21
        )
        
    quiver_scale_large_area = config['quiver_scale_large_area']
    if not isinstance(quiver_scale_large_area, float):
        util.error_msg(
            f'`quiver_scale_large_area` must be a float, '
            f'got {type(quiver_scale_large_area).__name__}',
            22
        )
        


    # precision to round significant digits
    precision = config['precision']
    if not isinstance(precision, int):
        util.error_msg(
            f'`precision` must be an integer, got {type(precision).__name__}',
            23
        )
    precision = int(precision)
    
    
    # show arguments in console and processing messages
    verbose = config['verbose']
    if not isinstance(verbose, bool):
        util.error_msg(
            f'`verbose` must be boolean, got {type(verbose).__name__}',
            24
        )
    verbose = bool(verbose)       
    
    
    # initialize dictionary
    config = {
        'sar_drift_directory': sar_drift_directory,
        'sar_drift_file': sar_drift_file,
        'sar_geotiff_file': sar_geotiff_file,
        'netcdf_cdl_file': netcdf_cdl_file,
        'output_dir': output_dir,
        'formatted_data_dir': formatted_data_dir,
        'gpkg_dir': gpkg_dir,
        'nc_dir':nc_dir,
        'png_dir': png_dir,
        'batch_process': batch_process,
        'delimiter': delimiter,
        'skip_rows_before_header': skip_rows_before_header,
        'detect_outliers': detect_outliers,
        "ignore_vector_threshold": ignore_vector_threshold,
        'use_geotiff': use_geotiff,
        'create_region_plot': create_region_plot,
        'vector_stride': vector_stride,
        'inlier_vector_stride': inlier_vector_stride,
        'quiver_scale_small_area': quiver_scale_small_area,
        'quiver_scale_large_area': quiver_scale_large_area,
        'precision': precision,
        'verbose': verbose
    }
            
    # log settings
    param_string = (
        "CONF PARAMS:\n"
        "  sar drift directory:     "
        f"{config['sar_drift_directory']}\n"
        "  sar drift file:          "
        f"{config['sar_drift_file']}\n"
        "  sar geotiff file:        "
        f"{config['sar_geotiff_file']}\n"
        "  NetCDF CDL file:         "
        f"{config['netcdf_cdl_file']}\n"
        "  output directory:        "
        f"{config['output_dir']}\n"
        "  batch process:           "
        f"{config['batch_process']}\n"
        "  delimiter:               "
        f"`{config['delimiter']}`\n"
        "  skip rows before header: "
        f"{config['skip_rows_before_header']}\n"
        "  use geotiff image:       "
        f"{config['use_geotiff']}\n"
        "  detect outliers:         "
        f"{config['detect_outliers']}\n"
        "  ignore vector threshold: "
        f"{config['ignore_vector_threshold']}\n"        
        "  create region plot:      "
        f"{config['create_region_plot']}\n"
        "  vector stride:           "
        f"{config['vector_stride']}\n"
        "  inlier vector stride:    "
        f"{config['inlier_vector_stride']}\n"        
        "  quiver scale small area: "
        f"{config['quiver_scale_small_area']}\n"
        "  quiver scale large area: "
        f"{config['quiver_scale_large_area']}\n"        
        "  precision:               "
        f"{config['precision']}\n"
    )
    if config['verbose'] is True:
        print(param_string)
    
    
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
    from datetime import datetime
    
    # parse user arguments
    config = read_json_config()

    files= []
    if config['batch_process']:
        all_files = glob(os.path.join(config['sar_drift_directory'], '*'))
        for file in all_files:
            if ('.txt' in file) or ('.csv' in file):
                files.append(file)
    else:
        files = [config['sar_drift_file']]
    
    
    for data_file in tqdm(files, desc='Processing data files...'):
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
        the dates in the file typically is the end date of the observation period
        https://osisaf-hl.met.no/sites/osisaf-hl/files/user_manuals/
        osisaf_pum_sea-ice-drift-lr_v1p9.pdf
        (Page 25)
        
        Version `0` indicates first process wihtout cleaned data
        
        For multiple pairs in one period, have included start/end date/time
        """
        start_min = df_sar['Date1'].min()
        start_date_time = datetime.strptime(
            start_min, "%Y-%m-%d %H:%M:%S"
        ).strftime("%Y%m%d_%H%M%S")

        end_max = df_sar['Date2'].max()
        end_date_time = datetime.strptime(
            end_max, "%Y-%m-%d %H:%M:%S"
        ).strftime("%Y%m%d_%H%M%S")
        
        output_basename = (
            f"SIVelocity_SAR_{start_date_time}_{end_date_time}_v0"
        )
    
    
        # Create shape file package for QGIS    
        gdf_points, gdf_lines = util.create_shape_package(
            df=df_sar,
            base_name=output_basename,
            config=config
        )
        
        
        # Create NetCDF file for QGIS    
        util.create_netcdf(
            df=df_sar,
            base_name=output_basename,
            config=config
        )
        
        continue
        
        
        # Overlay SAR drift data vectors on geotiff image
        util.overlay_sar_drift_on_geotiff(
            config=config,
            gdf_lines=gdf_lines,
            df_sar=df_sar,
            base_name=output_basename
        )
        
        exit()
        
        # Detect outliers
        if config['detect_outliers']:
            util.detect_outliers(
                config=config,
                outlier_type='sd'
            )
    
    
    
if __name__ == "__main__":
    main()
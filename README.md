# SAR Drift Output Generator

## Project Overview

This project converts daily SAR-derived sea ice drift data into GIS-ready formats:

- **GeoPackage (`.gpkg`)**: Contains point and line geometries representing ice drift observations.
- **NetCDF (`.nc`)**: CF/ACDD-compliant output including spatial grid of drift vectors (`dx`, `dy`), speed, and bearing.
- **PNG Plot (`.png`)**: High-resolution plot showing the SAR backscatter image with drift vectors and an overview map of the Arctic region.

The tool supports data visualization in QGIS and other NetCDF/GIS software, and it aligns SAR imagery with derived vector data using EPSG:3413 (NSIDC Sea Ice Polar Stereographic North). Update the parameters in the configuration JSON file to run locally. The script will create a NetCDF, a GeoPackage and a PNG file. If available, a GeoTIFF will appear under the SAR drift vectors. A regionaly map will optionally be created for reference. The entire Arctic region can also be displayed as well as specific areas of interest (depending on scope of the SAR drift datas file).

---

## Features

- Extracts and cleans drift data from `.txt` files
- Computes duration, distance, and azimuth per observation
- Converts lat/lon to projected `x/y` in meters using EPSG:3413
- Builds gridded NetCDF output with CF/ACDD metadata via `.cdl` files
- Generates GeoPackage output for GIS visualization

---

## Requirements

Install dependencies via:

```bash
pip install -r requirements.txt
conda install -c conda-forge gdal
```

Or use a Conda environment (recommended):

```bash
conda env create -f environment.yml
conda activate sar_drift
```

---

### Dependencies

- numpy
- pandas
- xarray
- geopandas
- shapely
- pyproj
- netCDF4
- scipy

You also need `ncgen` from the [NetCDF-C tools](https://www.unidata.ucar.edu/software/netcdf/) for CDL file parsing.
```bash
conda install -c conda-forge netcdf4
conda install -c conda-forge nco
ncgen -h
ncdump -h
ncks --version
```

---

## Metadata Injection via CDL

The script supports injecting metadata from a CDL file. It uses:

- `ncgen` to convert a `.cdl` template into a `.nc` file
- `xarray` to read and apply global attributes
- Placeholder replacement for fields like `FILL_DATE_CREATED`, `FILL_MIN_TIME`

Ensure your `.cdl` file lives in a directory (default: `meta/`) and follows CF/ACDD conventions.

---

## Running the Script

```bash
python sar_drift_output.py [options]
```

---

### JSON Parameters:
  - `sar_drift_filename`: Path to SAR drift data file.
  - `delimiter`: Character that separates the fields in the input data file (default: `,` [use `\t` for tab]).
  - `sar_geotiff_filename`: Path to GeoTIFF SAR image.
  - `use_geotiff`: Display the supplied GeoTIFF SAR image under the drift vectors. (Boolean)
  - `output_dir`: Directory for `.nc`, `.gpkg` and `.png` output.
  - `netcdf_cdl_file`: Defintion file for the NetCDF metadata standards.
  - `create_region_plot`: Display a regional map that indicates where are the drift vectors. (Boolean)
  - `vector_stride`: Offset of SAR drift vectors to plot from the input file. For many observations, increasing the stride results in less clutter. (Integer)
  - `quiver_scale`: Relative size of arrows on the plot. For smaller regions, 1.0 looks best. For larger regions, consider decreaing the factor to 0.2. (Float)
  - `precision`: Decimal precision (number of digits after decimal) for numeric output (Integer)
  - `verbose`: Display parameters and processing messages. (Boolean)

---

### Example:

```bash
python sar_drift_output.py -c config.json
```

---

## Input Files
- SAR Drift CSV: A .txt or .csv file with columns including:
    -  Lon1, Lat1, Lon2, Lat2: start and end coordinates
	-  Time1_JS, Time2_JS: Julian seconds since 2000-01-01
    -  U_vel_ms, V_vel_ms: velocity components
	-  Bear_deg, Speed_kmdy: bearing and speed
- GeoTIFF Image: Raster product of SAR backscatter with GCPs
- CDL File: Metadata template used to apply CF-compliant global and variable attributes to the NetCDF output
	
## Output
| Type                         | Description                                                                          |
| ---------------------------- | ------------------------------------------------------------------------------------ |
| `sar_drift_<timestamp>.gpkg` | QGIS GeoPackage with start points, end points, and drift lines                       |
| `sar_drift_<timestamp>.nc`   | CF/ACDD-compliant NetCDF with drift variables (`dx`, `dy`, `Speed_kmdy`, `Bear_deg`) |
| `sar_drift_<timestamp>.png`  | Annotated PNG showing SAR image and vector overlays                                  |
|							   |	  - Left: Arctic overview (Cartopy, EPSG:4326) with bounding box                  |
|							   |	  - Right: SAR image overlaid with quiver arrows, True North arrow, and scale bar |

---

## Notes

- The NetCDF file uses EPSG:3413 with properly defined grid_mapping attributes.
- GeoTIFF is reprojected using Ground Control Points (GCPs) via rasterio.
- Vector drift observations are rendered using LineString geometries with corresponding start points.
- Placeholder CDL values like FILL_DATE_CREATED are auto-filled during export.
- For full documentation, see inline docstrings in sar_drift.py and util.py.

---

## Return codes
- 01: Missing command-line argument for configuration JSON file.
- 02: Configuration JSON file is missing required parameters.
- 03: Unexpected parameters found in configuration JSON file.
- 04: Cannot locate SAR drift data file.
- 05: Cannot locate GeoTIFF file.
- 06: `use_geotiff` parameter must be Boolean (true|false).
- 07: Cannot locate output directory.
- 08: Cannot locate CDL file that meets NetCDF metadata standards.
- 09: `create_region_plot` parameter must be Boolean (true|false).
- 10: `vector_stride` parameter must be Integer (e.g. 8)
- 11: `vector_stride` cannot be less than 1, which is the minimum (no stride).
- 12: `quiver_scale` must be Float. The larger the plot region, the smaller the scale (e.g. Artice Region should have scale around 0.2, vectors disaplyed on top of GeoTIFF should have scale 1.0).
- 13: `precision` parameter must be Integer (e.g. 3).
- 14: `verbose` parameter must be Boolean (true|false).
- 15: The delimited SAR drift data file could not be properly parsed. Most likely, an incorrect delimiter character has been set as the `delimiter` character. For tab character, use `\t`.
- 16: Error running `ncgen` utility. Refer to `Dependencies` section if `nco` was not installed.

---

## License

This project is licensed under the MIT License.

---

## Contact

- Brendon Gory — [brendon.gory@noaa.gov](mailto:brendon.gory@noaa.gov)

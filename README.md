# SAR Drift Converter & Outlier Tools

This repository converts **SAR sea‑ice drift "gfilter" text outputs** into GIS- and analysis-ready products:

- **Formatted CSV** (cleaned/consistent columns)
- **GeoPackage (`.gpkg`)** with start points, end points, and drift lines (EPSG:3411)
- **NetCDF (`.nc`)** on a regular grid with metadata populated from a **CDL template**
- **STAC JSON** (`collection.json`, `items.json`, per-file `.json`) for catalog integration
- Optional utilities: vector PNGs, GeoTIFF overlays, and outlier detection (standard deviation or Mahalanobis)

---

## Requirements

Python environment:

- `cartopy`
- `dask` (used by xarray)
- `geopandas`
- `pandas`
- `matplotlib`
- `matplotlib-map-utils`
- `matplotlib-scalebar`
- `netCDF4`
- `numpy`
- `pyproj`
- `rasterio`
- `scikit-learn` (for `MinCovDet`)
- `scipy`
- `shapely`
- `tqdm`
- `xarray`

> **Note:** `cartopy`/`geopandas` are easiest via **conda-forge**.

---

## Configuration (`config.json`)

All runs are driven by a JSON config file.

### Input / batch settings
- `batch_process` (bool): process all csv or txt files in `sar_drift_directory`
- `sar_drift_directory` (str): input directory
- `sar_drift_filename` (str): process specific file
- `delimiter` (str): input delimiter (e.g. `","`)
- `skip_rows_before_header` (int): how many lines to skip before the header row
- `ignore_vector_threshold` (int): discard scenes with too many invalid vectors (see notes)

### Output directories / templates
- `output_dir` (str): top-level output directory
- `formatted_data_dir` (str): folder for cleaned CSV
- `gpkg_dir` (str): folder for GeoPackages
- `nc_dir` (str): folder for NetCDF
- `nc_cdl_template_file` (str): CDL template used to populate metadata
- `precision` (int): number of significant digits for numeric values in data and computations

### Optional plotting / overlays
- `use_geotiff` (bool): enable GeoTIFF overlay workflow (see note below)
- `sar_geotiff_file` (str): GeoTIFF file pattern/path used for overlays
- `create_region_plot` (bool): create regional overview plot (utility function)
- `use_vector_plot` (bool): create vector PNGs
- `quiver_scale_large_area`, `quiver_scale_small_area` (numbers): quiver scaling presets
- `include_gridlines` (bool): add map gridlines
- `vector_stride` (int): downsample stride for plotting (global)
- `inlier_vector_stride` (int): downsample stride used in inlier plots

### Outlier detection controls
- `z_score_level` (float): value where z-score above will be flagged as an outlier
- `chi_square_level` (float): chi-square tail probability [0 - 1] for Mahalanobis Distance outlier
- `neighbor_radius_km` (float): distance from observation to find neighbors
- `min_neighbors` (int): minimum neighbors to mark a z-score result as statistically confident
- `md_min_neighbors` (int): minimum neighbors to mark a Mahalanobis Distance result as statistically confident
- `outlier_passes` (int): number of passes to detect outlier; each pass removes an identified outlier from the pool of neighbors

### Versions

| Version | Filtering | Output|
|---------|-----------|-------|
|`00`| Testing | Testing |
|`01`| - Remove observations where `BearDeg`=0 | NetCDF |
| | - Skip 75km files where `MaxCorr1` > `MaxCorr2` percentage < 60% correct| |
|`02`| - Remove observations where `BearDeg`=0 | Outlier labels in NetCDF |
| | - Skip 75km files where `MaxCorr1` > `MaxCorr2` percentage < 60% correct | Outlier labels in GeoPackage|
| |- Skip files where observations are below predefined threshold| |
|`03`| - Remove observations where `BearDeg`=0 | No outliers in NetCDF |
| | - Skip 75km files where `MaxCorr1` > `MaxCorr2` percentage < 60% correct | No outliers in GeoPackage|
| |- Skip files where observations are below predefined threshold | No outliers in PNG/SVG/Plotly|

---

## Usage

### Convert SAR drift text → CSV + GeoPackage + NetCDF

From the repo root:

```bash
python sar_drift_converter.py
```

`sar_drift_converter.py` loads `config.json` by default. The script:

1. Glob-matches input files from `sar_drift_directory` / `sar_drift_filename`
2. Reads the gfilter drift text into a dataframe
3. Writes:
   - formatted CSV
   - GeoPackage with 3 layers (`start_points`, `end_points`, `drift_lines`)
   - NetCDF output with grid + metadata from the CDL template

Output filenames are derived from the input basename.

---

### Generate STAC JSON

After producing output files, `create_json_for_stac(config)` generates the full STAC catalog structure for the collection. It is called automatically at the end of a converter run.

It produces:

- **Per-file item JSON** (e.g. `SIVelocity_SAR_20241014_20241015_daily_12km_NH_v01_nc.json`) — one per output file (NetCDF, GeoPackage, and/or HTML depending on version)
- **`items.json`** — a GeoJSON `FeatureCollection` of all items
- **`collection.json`** — the STAC collection with temporal extent derived from the output files

All files are written to:
```
polarwatch/stac/collections/sar_drift_ice_velocities_v{version}/
```

#### File types per version

| Version | NetCDF | GeoPackage | HTML |
|---------|--------|------------|------|
| `01` | ✓ | | |
| `02` | ✓ | ✓ | |
| `03` | ✓ | ✓ | ✓ |

#### Asset MIME types

| Extension | `type` |
|-----------|--------|
| `.nc` | `application/x-netcdf` |
| `.gpkg` | `application/vnd.sqlite3` |
| `.html` | `text/html` |

#### Serving files locally

Asset `href` values are set to `http://localhost:8001/<filename>`. To make files accessible, run a second HTTP server from the output directory:

```bash
cd D:\NOAA\GitHub\sar_drift_converter\v01
python -m http.server 8001
```

> **Note:** `file:///` URLs are blocked by browsers even on localhost. The `http://localhost` approach is required for download links to work in the STAC viewer.

#### Date parsing

Start and end datetimes are parsed from output filenames using the pattern `_YYYYMMDD_`. For example:

```
SIVelocity_SAR_20241014_20241015_daily_12km_NH_v01.nc
                ↑ start     ↑ end
```

---

## Outputs

Given an input like:

```
RCM1_SHUB_2024_10_15_02_13_41_..._vel_1.01d_0050000m_0000500m.txt_0
```

you should expect (directories from `config.json`):

- `formatted_data/<basename>.csv`
- `gpkg/<basename>.gpkg`
- `nc/<basename>.nc`
- `polarwatch/stac/collections/sar_drift_ice_velocities_v{version}/<basename>_nc.json`
- `polarwatch/stac/collections/sar_drift_ice_velocities_v{version}/items.json`
- `polarwatch/stac/collections/sar_drift_ice_velocities_v{version}/collection.json`

---

## Variable Reference

Variables flow through three stages: raw columns read from the CSV source file, derived columns computed during pipeline processing, and variables written to the NetCDF and GeoPackage outputs.

### CSV source — raw input columns

Columns marked *dropped* are consumed during processing but not carried forward into any output file.

| Column | Units | Retained | Description |
|--------|-------|----------|-------------|
| `File1` | — | ✓ | Filename of the first SAR scene (start image) |
| `File2` | — | ✓ | Filename of the second SAR scene (end image) |
| `Time1_JS` | s | dropped | Start time as Julian seconds since 2000-01-01 00:00:00 |
| `Time2_JS` | s | dropped | End time as Julian seconds since 2000-01-01 00:00:00 |
| `Lon1` | degrees | renamed → `longitude_1` | Starting longitude of the tracked ice feature |
| `Lat1` | degrees | renamed → `latitude_1` | Starting latitude of the tracked ice feature |
| `Lon2` | degrees | renamed → `longitude_2` | Ending longitude of the tracked ice feature |
| `Lat2` | degrees | renamed → `latitude_2` | Ending latitude of the tracked ice feature |
| `Bear_deg` | degrees | dropped | Source-file bearing; used in `filter_input_data` to remove zero-bearing rows, then dropped |
| `Speed_kmdy` | km/day | dropped | Source-file speed; used in `filter_input_data` for speed threshold filtering, then dropped |
| `U_vel_ms` | m s⁻¹ | dropped | Source-file x-velocity component; dropped after read (recomputed from projected coordinates) |
| `V_vel_ms` | m s⁻¹ | dropped | Source-file y-velocity component; dropped after read (recomputed from projected coordinates) |
| `Maxcorr1` | — | ✓ | Cross-correlation score of the first (lower-ranked) match candidate |
| `Maxcorr2` | — | ✓ | Cross-correlation score of the second (best) match candidate; must exceed `Maxcorr1` for the row to pass filtering |
| `img1_mean`, `img1_std` | — | dropped | Image 1 patch mean and standard deviation |
| `img2_mean`, `img2_std` | — | dropped | Image 2 patch mean and standard deviation |
| `img1s_mean`, `img1s_std` | — | dropped | Image 1 sub-patch mean and standard deviation |
| `Npnt` | — | dropped | Number of points used in the correlation |
| `Offset1`, `Offset2` | — | dropped | Correlation offset values |

### Derived — computed in pipeline

These columns are added by `read_sar_drift_data_file` and `outlier_search` and are carried through all downstream processing.

| Column | CRS / Reference | Units | Description |
|--------|----------------|-------|-------------|
| `date_start` | — | — | Start datetime converted from `Time1_JS` (format: `YYYY-MM-DD HH:MM:SS`) |
| `date_end` | — | — | End datetime converted from `Time2_JS` |
| `duration_s` | — | s | Observation duration (`Time2_JS − Time1_JS`) |
| `longitude_1` | EPSG:4326 | degrees | Starting longitude (renamed from `Lon1`) |
| `latitude_1` | EPSG:4326 | degrees | Starting latitude (renamed from `Lat1`) |
| `longitude_2` | EPSG:4326 | degrees | Ending longitude (renamed from `Lon2`) |
| `latitude_2` | EPSG:4326 | degrees | Ending latitude (renamed from `Lat2`) |
| `sensor1` | — | — | Satellite identifier extracted from `File1` (prefix before first underscore) |
| `sensor2` | — | — | Satellite identifier extracted from `File2` |
| `X1` | EPSG:3413 | m | Projected x-coordinate of start position |
| `Y1` | EPSG:3413 | m | Projected y-coordinate of start position |
| `X2` | EPSG:3413 | m | Projected x-coordinate of end position |
| `Y2` | EPSG:3413 | m | Projected y-coordinate of end position |
| `sea_ice_x_displacement` | EPSG:3413 | m | X displacement (`X2 − X1`) |
| `sea_ice_y_displacement` | EPSG:3413 | m | Y displacement (`Y2 − Y1`) |
| `u_vel_ms` | EPSG:3413 | m s⁻¹ | X-component of velocity (`sea_ice_x_displacement / duration_s`) |
| `v_vel_ms` | EPSG:3413 | m s⁻¹ | Y-component of velocity (`sea_ice_y_displacement / duration_s`) |
| `sea_ice_speed` | geodesic | m s⁻¹ | Drift speed from geodesic distance / `duration_s` |
| `sea_ice_speed_kmdy` | geodesic | km/day | Drift speed in km/day from geodesic distance |
| `direction_of_sea_ice_displacement` | geodesic | degrees | Forward azimuth from geodesic inverse calculation (WGS84) |
| `distance` | geodesic | m | Geodesic distance between start and end positions (WGS84) |
| `outlier_category` | — | — | Two-digit outlier code (see [Outlier detection](#outlier-detection-optional)); fill = `−9` (version `01`) |
| `bearing_error` | — | — | `1` if `direction_of_sea_ice_displacement == 0` or `sea_ice_speed == 0`; `0` = valid; `−9` = not computed (versions `02`/`03`) |
| `speed_error` | — | — | `1` if speed exceeds threshold (25 km/day for 50 km files; 35 km/day for 75 km files); `0` = valid; `−9` = not computed (versions `02`/`03`) |
| `measurement_error` | — | — | `1` if `Maxcorr1 > Maxcorr2`; `0` = valid; `−9` = not computed (versions `02`/`03`) |

### NetCDF output variables

All gridded data variables have dimensions `(time, y, x)` projected on the NSIDC 12.5 km polar stereographic grid (EPSG:3413). Coordinates and auxiliary variables are also listed.

| Variable | Dimensions | Type | Units | Description |
|----------|------------|------|-------|-------------|
| `sea_ice_speed` | (time, y, x) | float32 | m s⁻¹ | Gridded sea ice drift speed |
| `sea_ice_x_displacement` | (time, y, x) | float32 | m | X-component of ice displacement |
| `sea_ice_y_displacement` | (time, y, x) | float32 | m | Y-component of ice displacement |
| `direction_of_sea_ice_displacement` | (time, y, x) | float32 | degrees | Drift direction (forward azimuth) |
| `outlier_category` | (time, y, x) | int16 | — | Outlier classification code; fill value = `−9` |
| `bearing_error` | (time, y, x) | int16 | — | Bearing validity flag; fill value = `−9` |
| `speed_error` | (time, y, x) | int16 | — | Speed threshold flag; fill value = `−9` |
| `measurement_error` | (time, y, x) | int16 | — | Cross-correlation quality flag; fill value = `−9` |
| `spatial_ref` | scalar | int32 | — | CRS container variable holding WKT/proj4 projection metadata |
| `time_bnds` | (time, nv=2) | float64 | s | CF time bounds: `[min(date_start), max(date_end)]` in seconds since 2000-01-01 |
| `time` *(coord)* | (time) | float64 | s | Scene reference time: `min(date_start)` in seconds since 2000-01-01 |
| `x` *(coord)* | (x) | float64 | m | EPSG:3413 x-coordinates of the 12.5 km polar stereographic grid |
| `y` *(coord)* | (y) | float64 | m | EPSG:3413 y-coordinates of the 12.5 km polar stereographic grid |

### GeoPackage output columns

Layer name: `drift_lines`. CRS: EPSG:3413. Geometry: `LineString` from `(X1, Y1)` to `(X2, Y2)` in projected metres.

| Column | CRS / Reference | Units | Description |
|--------|----------------|-------|-------------|
| `sensor1` | — | — | Satellite identifier for the start scene |
| `sensor2` | — | — | Satellite identifier for the end scene |
| `longitude_1` | EPSG:4326 | degrees | Starting longitude |
| `latitude_1` | EPSG:4326 | degrees | Starting latitude |
| `longitude_2` | EPSG:4326 | degrees | Ending longitude |
| `latitude_2` | EPSG:4326 | degrees | Ending latitude |
| `X1` | EPSG:3413 | m | Projected x-coordinate of start position |
| `Y1` | EPSG:3413 | m | Projected y-coordinate of start position |
| `X2` | EPSG:3413 | m | Projected x-coordinate of end position |
| `Y2` | EPSG:3413 | m | Projected y-coordinate of end position |
| `date_start` | — | — | Start datetime string (`YYYY-MM-DD HH:MM:SS`) |
| `date_end` | — | — | End datetime string (`YYYY-MM-DD HH:MM:SS`) |
| `duration_s` | — | s | Observation duration in seconds |
| `sea_ice_x_displacement` | EPSG:3413 | m | X displacement (matches NetCDF variable) |
| `sea_ice_y_displacement` | EPSG:3413 | m | Y displacement (matches NetCDF variable) |
| `u_vel_ms` | EPSG:3413 | m s⁻¹ | X-component of velocity |
| `v_vel_ms` | EPSG:3413 | m s⁻¹ | Y-component of velocity |
| `sea_ice_speed` | geodesic | m s⁻¹ | Drift speed (matches NetCDF variable) |
| `sea_ice_speed_kmdy` | geodesic | km/day | Drift speed in km/day |
| `direction_of_sea_ice_displacement` | geodesic | degrees | Drift direction (matches NetCDF variable) |
| `distance` | geodesic | m | Geodesic displacement distance |
| `outlier_category` | — | — | Two-digit outlier code; included only in versions `00` and `02` |
| `geometry` | EPSG:3413 | — | `LineString` from `(X1, Y1)` to `(X2, Y2)` in projected metres |
| `geometry_type` | — | — | Literal string `'line'` identifying the layer geometry type |

---

## Outlier detection (optional)

The main outlier routine is implemented in `util.outlier_search(...)` and supports:

- Standard deviation distance/bearing z-score based. Threshold can be set in configuration file (default 3)
- `outlier_type="md"`: robust Mahalanobis distance (`MinCovDet`) on features like
  `U_kmdy`, `V_kmdy`

Key ideas:

- Neighbors are found **within each "scene"** (grouped by `File1`, `File2`)
- Neighborhoods are computed with a **radius search** (km) using `cKDTree.query_ball_point`
- `outlier_category` (under / meets neighbor threshold) encodes **type** and **statistical confidence**:

| Code | Outlier Type | Neighbor Threshold Met |
|------|-------------|----------------------|
| `00` | None | No |
| `01` | None | Yes |
| `10` | Distance | No |
| `11` | Distance | Yes |
| `20` | Bearing | No |
| `21` | Bearing | Yes |
| `30` | Mahalanobis Distance | No |
| `31` | Mahalanobis Distance | Yes |
| `40` | Distance and Bearing | No |
| `41` | Distance and Bearing | Yes |
| `50` | Mahalanobis Distance and Distance | No |
| `51` | Mahalanobis Distance and Distance | Yes |
| `60` | Mahalanobis Distance and Bearing | No |
| `61` | Mahalanobis Distance and Bearing | Yes |
| `70` | Mahalanobis Distance, Distance and Bearing | No |
| `71` | Mahalanobis Distance, Distance and Bearing | Yes |

### Iterative option

For each pass in `outlier_passes`, only vectors with `outlier_category in ["00", "01"]`
are used as the pool when recomputing neighbors each iteration. This prevents already-flagged
vectors from influencing local statistics while still keeping all original rows in the output
(for geopackage tracking). By default, iterations will be set to one extra pass after the
first outlier check.

---

## GeoTIFF overlays and regional plots (optional)

`util.py` also includes:

- `overlay_sar_drift_on_geotiff(config, gdf_lines, df_sar, base_name)`
- `create_region_plot(config, base_name, bounds, gdf_lines=None)`

These require `matplotlib` and `cartopy` (and GeoTIFF tooling where applicable).

---

## Output quality notes

- **Quiver units:** `dx/dy` are in **meters** if built from EPSG:3411 coordinates.
  Adjust `scale` and `width` accordingly.
- **Zero std:** guard against `dist_std==0` or `bear_std==0` to avoid divide-by-zero.
- **"Pick up sticks" scenes:** If a scene has many invalid vectors (e.g., low correlation),
  it's often best to discard that scene. Use `ignore_vector_threshold` and/or
  a "% correct" rule (e.g., `(Maxcorr2 > Maxcorr1)` fraction) upstream.

---

## Notebooks

### `sar_sea_ice_drift_netcdf_layer_viewer.ipynb`

An interactive Jupyter notebook for exploring and exporting individual time layers from the daily SAR sea-ice drift NetCDF product.

**What it does:**

- Opens a NetCDF file and displays a high-level dataset summary
- Lists all `layer_id` values so a layer can be located by scene ID or index
- Computes per-variable statistics (shape, valid count, min/max/mean/std) for a selected layer
- Exports a selected layer to a **GeoPackage** (`drift_lines`, EPSG:3413) with an embedded QGIS QML style
- Renders a **quiver plot PNG** of drift vectors on a polar stereographic basemap

**Key parameters (set by the user):**

| Parameter | Description |
|-----------|-------------|
| `nc_path` | Path to the input NetCDF file |
| `selected_layer_index` | Integer index of the time layer to export/plot |
| `has_outliers` | `True` for version `02` files (colors arrows by outlier category); `False` for versions `01`/`03` (colors by displacement magnitude) |

**Outputs written to disk:**

| File | Location | Description |
|------|----------|-------------|
| `<layer_id>.gpkg` | `layer_to_gpkg/` | GeoPackage with `drift_lines` layer and embedded QML style |

The PNG plot can be saved locally by right-clicking the inline image and choosing *Save Image As*.

**Dependencies:** See [Requirements](#requirements). The notebook includes an install cell (set to `Raw NBConvert` by default — change to `Code` to run).

---

## Quick checklist

1. Update `config.json` paths (`sar_drift_directory`, output dirs, CDL template)
2. Run `python sar_drift_converter.py`
3. Open `.gpkg` in QGIS (EPSG:3411) to verify vector placement
4. Validate `.nc` metadata and grid
5. Start local file server (`python -m http.server 8001`) from the output directory
6. Open STAC viewer at `http://localhost:8000` and verify collection and item links
7. Enable outlier/plotting utilities as needed

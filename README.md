# SAR Drift Converter

This repository converts **SAR sea-ice drift "gfilter" text outputs** into GIS- and analysis-ready products:

- **Formatted CSV** (cleaned/consistent columns)
- **GeoPackage (`.gpkg`)** with drift lines in a configurable projected CRS — for levels `00`/`02`, one layer per scene per day; for level `03`, one combined daily layer
- **NetCDF (`.nc`)** on a regular grid with metadata populated from a **CDL template** — two files per day: a multi-layered scenes file (one time layer per scene pair) and a single-layer daily summary
- **Interactive vector HTML** — one file per level/EPSG combination, with per-day JSON data files (levels `00` and `03` only)
- **Buoy drift JSON** — per-day JSON files from UW IABP buoy observations, served alongside SAR vectors in the HTML viewer
- Outlier detection (z-score and Mahalanobis) and buoy data download/processing utilities

---

## Requirements

Two dependency files are provided. Use whichever matches your workflow:

**`environment.yml`** (conda, recommended):

```bash
conda env create -f environment.yml
conda activate sar_drift_converter
```

**`requirements.txt`** (pip):

```bash
pip install -r requirements.txt
```

### Package list

| Package |  Notes |
|---------|--------|
| `beautifulsoup4` | HTML parsing for SAR drift file download |
| `cartopy` | Cartopy basemap rendering in the layer viewer notebook; not required by the main pipeline |
| `geopandas` | GeoPackage output |
| `matplotlib` | Quiver plot rendering in the layer viewer notebook; not required by the main pipeline |
| `nc-time-axis` | NetCDF time axis support; installed via pip in both environments |
| `netCDF4` | NetCDF read/write |
| `numpy` | Numerical computation |
| `pandas` | DataFrame processing |
| `pyproj` | CRS transformation |
| `python=3.10` | Minimum Python version (conda only) |
| `rasterio>=1.3.0` | Raster I/O |
| `requests` | HTTP file downloads |
| `scikit-learn` | `LedoitWolf` covariance for Mahalanobis outlier detection |
| `scipy` | Statistical functions |
| `shapely` | Geometry construction |
| `tqdm` | Progress bars |
| `urllib3` | HTTP utilities (SSL warning suppression) |
| `xarray` | NetCDF dataset handling |

> **Note:** `geopandas` and `cartopy` install most reliably via **conda-forge**; pip users may encounter compilation errors for these two packages. `cartopy` and `matplotlib` are only required by the layer viewer notebook, not by the main pipeline script. `nc-time-axis` is installed via pip in both environments since it is not available on conda-forge.

---

## Configuration (`config.json`)

All runs are driven by a JSON config file passed via `-c config.json`. Every key listed below is required — the script will exit with an error if any key is missing or unexpected. Keys beginning with `_comment` are permitted and silently ignored.

### Input / batch settings

| Key | Type | Description |
|-----|------|-------------|
| `batch_process` | bool | If `true`, process all `.txt`/`.csv` files in `sar_drift_directory`; if `false`, process the single file at `sar_drift_filename` |
| `sar_drift_directory` | str | Directory containing gfilter input files (used when `batch_process` is `true`) |
| `sar_drift_filename` | str | Path to a single gfilter input file (used when `batch_process` is `false`) |
| `delimiter` | str | Field separator in the input file (e.g. `","`, `"\\t"`) |
| `sar_drift_data_url` | str | URL of the directory listing page hosting SAR drift gfilter text files; scraped at startup to download new files |
| `uw_iabp_buoy_url` | str | URL hosting UW IABP buoy observation data |
| `uw_iabp_buoy_tables` | str | URL of the `.js` file listing active buoy identifiers |
| `uw_iabp_buoy_filename` | str | Base filename for the downloaded buoy CSV (date range is appended automatically) |

### Output paths and templates

| Key | Type | Description |
|-----|------|-------------|
| `file_server` | str | Root path where daily outputs are written, structured as `<file_server>/<epsg>/<level_label>/<year>/<type>/` |
| `netcdf_cdl_file` | str | Path to the base CDL template file used to populate NetCDF metadata (e.g. `sar_drift_output.cdl`); the pipeline derives the EPSG-specific variant automatically (e.g. `sar_drift_output_3413.cdl`) |
| `netcdf_template_file` | str | Path to the NSIDC polar stereographic NetCDF template providing the target grid |
| `outlier_qml_file` | str | Path to QML style file for outlier-category coloring in QGIS (applied for level `02`) |
| `graduated_qml_file` | str | Path to QML style file for graduated-speed coloring in QGIS (applied for levels other than `02`) |
| `html_vector_template` | str | Filename of the HTML viewer template for the interactive drift vector map; must be present in `meta_dir` |
| `html_index_template` | str | Filename of the `index.html` template for the directory listing page; must be present in the project root or `meta_dir` |
| `webpage_folders` | list | Folder names (e.g. `["css", "js", "image", "webfonts"]`) copied from `meta_dir` to the file server to support the index page |
| `geojson_templates` | list | GeoJSON filenames (e.g. `["land.geojson", "10m_coastline_50N.geojson", "graticule_50N.geojson"]`) copied from `meta_dir` into each level's `data/` subdirectory at runtime |
| `meta_dir` | str | Directory containing all static reference files: CDL templates, HTML templates, QML styles, GeoJSON reference layers, and web support folders |
| `buoy_dir` | str | Directory where downloaded UW IABP buoy text files and the compiled buoy CSV are stored |
| `output_dir` | str | Parent directory for local intermediate outputs (e.g. `"level_output"`); per-level subdirectories are created beneath this path automatically |
| `log_dir` | str | Directory for the run log file (e.g. `"log"`); existing `.log` files are compressed to `.zip` at startup and a fresh timestamped log is created |

> **Note:** `formatted_data_dir`, `nc_dir`, and `filtered_data_dir` are **not** config.json keys. They are derived automatically by the script as subdirectories of `output_dir/<level>/`.

### Run controls

| Key | Type | Description |
|-----|------|-------------|
| `clear_output_dir` | bool | If `true`, delete `output_dir/<level>/` and all contents before the run |
| `overwrite` | bool | If `true`, rewrite all output files even if they already exist on disk |
| `reprocess_days` | int | Number of most-recent days to always reprocess regardless of whether outputs already exist; set to `0` to disable |
| `verbose` | bool | If `true`, print all resolved config parameters to stdout at startup |
| `version` | str | Version string included in output filenames (e.g. `"01"`) |

### Processing levels

Processing levels are dispatched internally by `process_level_output` and are not read from `config.json`.

| Level | Filtering | Outputs |
|-------|-----------|---------|
| `00` | None (diagnostic/testing) | NetCDF (scenes + daily), GeoPackage (per-scene layers), vector HTML/JSON |
| `01` | No hard row drops; bearing/speed/correlation quality captured as `bearing_error`, `speed_error`, `measurement_error` flags in NetCDF | NetCDF (scenes + daily) only |
| `02` | Per-row drops: zero bearing+speed simultaneously, speed above threshold, `Maxcorr2 ≤ Maxcorr1`. Scene-level rejection: <60% valid Maxcorr or too few vectors. Outlier detection applied | NetCDF (scenes + daily), GeoPackage (one layer per scene) |
| `03` | Same as `02`, plus inlier-only filtering: retain `outlier_category` `00`/`01`, recode to `−1` | NetCDF (scenes + daily), GeoPackage (combined daily layer), vector HTML/JSON (inliers only) |

---

## Algorithm Parameters (`constants.py`)

Versioned algorithm parameters are defined in `constants.py` so that changes are tracked under version control independently of `config.json`. These values are loaded at startup and cannot be overridden via `config.json`.

### Filtering

| Parameter | Default | Description |
|-----------|---------|-------------|
| `IGNORE_VECTOR_THRESHOLD` | `1` | Discard scenes whose remaining vector count falls at or below this value after per-row filtering |
| `Z_SCORE_LEVEL` | `2.75` | Z-score threshold above which a vector is flagged as a speed or bearing outlier |
| `CHI_SQUARE_LEVEL` | `0.975` | Chi-square cumulative probability used to derive the squared Mahalanobis distance cutoff (`chi2.ppf(CHI_SQUARE_LEVEL, df=2)`) |

### Neighbor search

| Parameter | Default | Description |
|-----------|---------|-------------|
| `NEIGHBOR_RADIUS_KM` | `25.0` | Radius in kilometres for spatial neighbor lookup via `cKDTree.query_ball_point` |
| `MIN_NEIGHBORS` | `8` | Minimum neighbors required to mark a z-score outlier result as statistically confident (units digit `1`) |
| `MD_MIN_NEIGHBORS` | `24` | Minimum neighbors required to mark a Mahalanobis distance outlier result as statistically confident |
| `OUTLIER_PASSES` | `3` | Maximum number of iterative outlier detection passes; iteration stops early if the inlier count stabilizes between passes |

### Rounding

| Parameter | Default | Columns affected |
|-----------|---------|-----------------|
| `COORDINATE_PRECISION` | `4` | `latitude_1`, `longitude_1`, `latitude_2`, `longitude_2`, `X1`, `Y1`, `X2`, `Y2` |
| `DISPLACEMENT_PRECISION` | `4` | `sea_ice_x_displacement`, `sea_ice_y_displacement`, `u`, `v` |
| `SPEED_PRECISION` | `1` | `sea_ice_speed`, `sea_ice_speed_kmdy`, `distance` |
| `BEARING_PRECISION` | `0` | `direction_of_sea_ice_displacement` |

> **Note:** Rounding is applied with `numpy.round()` immediately after computation. NetCDF variables are stored as `float32`; reading them back as `float64` before rounding in the notebook removes float32 binary representation noise.

---

## Usage

```bash
python sar_drift_converter.py -c config.json
```

The script:

1. Parses and validates `config.json` (`read_json_config`)
2. Compresses any existing `.log` files to `.zip` archives and initialises a fresh timestamped log file in `log_dir`
3. Downloads new SAR drift gfilter files from `sar_drift_data_url`; files already present locally are skipped; links returning HTTP 404 are logged and skipped
4. Glob-matches all `.txt`/`.csv` files from `sar_drift_directory` (batch mode) or loads the single file at `sar_drift_filename`
5. Reads all gfilter files in parallel into a single combined DataFrame; for each 50 km file, automatically substitutes the corresponding 75 km file if one exists
6. Drops duplicate rows and any observations where polarization is not HH in both `File1` and `File2`; the count of dropped observations is logged
7. Applies EPSG-dependent coordinate projection once per target EPSG (`_apply_projection`); EPSGs processed: `[3413, 6931]`
8. For levels `00` and `03`, downloads UW IABP buoy data, writes all per-day buoy JSON files, and updates the interactive HTML index file
9. For each level/EPSG combination, calls `create_level_output`:
   - Applies per-row and scene-level quality filters (`filter_input_data`)
   - Groups observations by calendar day of `date_start`
   - For each day, checks `_check_existing_files`; days within `reprocess_days` of today or where `overwrite` is `true` are always reprocessed; days where all outputs exist are skipped entirely
   - For each day requiring processing, runs outlier detection per scene and accumulates post-detection rows into `df_scenes`
   - Produces daily outputs from `df_scenes`: NetCDF (scenes + daily), GeoPackage, and vector HTML/JSON as applicable for the level

### Daily output filename convention

```
SIVelocity_SAR_<YYYYMMDD>_<YYYYMMDD>_<type>_12km_NH_<epsg>_PL<level>_v<version>.<ext>
```

where `<type>` is `scenes` for the multi-layered NetCDF and `daily` for all other output types. Files are written to:

```
<file_server>/<epsg>/<level_label>/<year>/<type>/
```

For example, a level `03` daily GeoPackage for 2024-12-30:

```
SIVelocity_SAR/3413/Processing Level - 03 (PL03)/2024/gpkg/SIVelocity_SAR_20241230_20241231_daily_12km_NH_3413_PL03_v01.gpkg
```

The interactive HTML viewer and its data files sit one level above the year directory:

```
SIVelocity_SAR/3413/Processing Level - 03 (PL03)/SIVelocity_SAR_interactive_vector_map.html
SIVelocity_SAR/3413/Processing Level - 03 (PL03)/data/si_velocity_<YYYYMMDD>.json
SIVelocity_SAR/3413/Processing Level - 03 (PL03)/data/buoy_velocity_<YYYYMMDD>.json
SIVelocity_SAR/3413/Processing Level - 03 (PL03)/data/available_dates.json
SIVelocity_SAR/3413/index.html
```

### Local output subdirectory structure

Created automatically under `output_dir/<level>/`:

| Directory | Contents |
|-----------|----------|
| `filtered_data/` | Unfiltered combined CSV (level `00` only) |
| `formatted_data/` | Per-scene formatted CSVs (level `00`); daily `_raw.csv` and `_processing_codes.csv` |
| `nc/` | Temporary intermediate NetCDF files used during daily mosaic construction |

Daily GeoPackage, vector HTML/JSON, and final NetCDF mosaics are written to `file_server` subdirectories, not to `output_dir/`.

---

## Outputs

For a batch run covering 2024-12-30 at level `03`:

**File server daily outputs** (`SIVelocity_SAR/3413/Processing Level - 03 (PL03)/`):
- `nc/SIVelocity_SAR_20241230_20241231_scenes_12km_NH_3413_PL03_v01.nc`
- `nc/SIVelocity_SAR_20241230_20241231_daily_12km_NH_3413_PL03_v01.nc`
- `gpkg/SIVelocity_SAR_20241230_20241231_daily_12km_NH_3413_PL03_v01.gpkg`
- `SIVelocity_SAR_interactive_vector_map.html`
- `data/si_velocity_20241230.json`
- `data/buoy_velocity_20241230.json`
- `data/available_dates.json`

**File server index** (`SIVelocity_SAR/3413/`):
- `index.html`
- `css/`, `js/`, `image/`, `webfonts/` (copied from `meta_dir`)

---

## Variable Reference

### CSV source — raw input columns

Columns marked *dropped* are consumed during processing but not carried forward into any output file.

| Column | Units | Retained | Description |
|--------|-------|----------|-------------|
| `File1` | — | ✓ | Filename of the first SAR scene (start image) |
| `File2` | — | ✓ | Filename of the second SAR scene (end image) |
| `Time1_JS` | s | dropped | Start time as Julian seconds since 2000-01-01 00:00:00 |
| `Time2_JS` | s | dropped | End time as Julian seconds since 2000-01-01 00:00:00 |
| `Lon1` | degrees | renamed → `longitude_1` | Starting longitude |
| `Lat1` | degrees | renamed → `latitude_1` | Starting latitude |
| `Lon2` | degrees | renamed → `longitude_2` | Ending longitude |
| `Lat2` | degrees | renamed → `latitude_2` | Ending latitude |
| `Bear_deg` | degrees | dropped | Source-file bearing; used to flag zero-bearing rows |
| `Speed_kmdy` | km/day | dropped | Source-file speed; used for speed threshold checks |
| `U_vel_ms` | m s⁻¹ | dropped | Source-file x-velocity; dropped after read (recomputed from projected coordinates) |
| `V_vel_ms` | m s⁻¹ | dropped | Source-file y-velocity; dropped after read |
| `Maxcorr1` | — | ✓ | Cross-correlation score of the first (lower-ranked) match candidate |
| `Maxcorr2` | — | ✓ | Cross-correlation score of the second (best) match candidate; must exceed `Maxcorr1` for the row to pass filtering |
| `img1_mean`, `img1_std` | — | dropped | Image 1 patch statistics |
| `img2_mean`, `img2_std` | — | dropped | Image 2 patch statistics |
| `img1s_mean`, `img1s_std` | — | dropped | Image 1 sub-patch statistics |
| `Npnt` | — | dropped | Number of points used in the correlation |
| `Offset1`, `Offset2` | — | dropped | Correlation offset values |

### Derived — computed in pipeline

| Column | CRS / Reference | Units | Description |
|--------|----------------|-------|-------------|
| `scene_id` | — | — | `File1_File2`; used to group observations into scene pairs |
| `date_start` | — | — | Start datetime converted from `Time1_JS` (`YYYY-MM-DD HH:MM:SS`) |
| `date_end` | — | — | End datetime converted from `Time2_JS` |
| `duration` | — | s | Observation duration (`Time2_JS − Time1_JS`) |
| `sensor1`, `sensor2` | — | — | Satellite identifiers extracted from `File1`/`File2` |
| `longitude_1`, `latitude_1` | EPSG:4326 | degrees | Start position; rounded to `COORDINATE_PRECISION` |
| `longitude_2`, `latitude_2` | EPSG:4326 | degrees | End position; rounded to `COORDINATE_PRECISION` |
| `X1`, `Y1` | EPSG:`config['epsg']` | m | Projected start position; rounded to `COORDINATE_PRECISION` |
| `X2`, `Y2` | EPSG:`config['epsg']` | m | Projected end position; rounded to `COORDINATE_PRECISION` |
| `sea_ice_x_displacement` | EPSG:`config['epsg']` | m | X displacement (`X2 − X1`); rounded to `DISPLACEMENT_PRECISION` |
| `sea_ice_y_displacement` | EPSG:`config['epsg']` | m | Y displacement (`Y2 − Y1`); rounded to `DISPLACEMENT_PRECISION` |
| `u` | EPSG:`config['epsg']` | m s⁻¹ | X-component of velocity; rounded to `DISPLACEMENT_PRECISION` |
| `v` | EPSG:`config['epsg']` | m s⁻¹ | Y-component of velocity; rounded to `DISPLACEMENT_PRECISION` |
| `sea_ice_speed` | geodesic | m s⁻¹ | Drift speed from geodesic distance / duration; rounded to `SPEED_PRECISION` |
| `sea_ice_speed_kmdy` | geodesic | km/day | Drift speed in km/day; rounded to `SPEED_PRECISION` |
| `direction_of_sea_ice_displacement` | geodesic | degrees | Forward azimuth (WGS84); rounded to `BEARING_PRECISION` |
| `distance` | geodesic | m | Geodesic distance between start and end positions; rounded to `SPEED_PRECISION` |
| `outlier_category` | — | — | Two-digit outlier code; `−1` = inlier filter applied (level `03`); `−9` = not computed (level `01`) |
| `bearing_error` | — | — | `1` if both bearing and speed are exactly zero simultaneously; `0` = valid; for levels `02`/`03`, always `0` since bad vectors are removed upstream |
| `speed_error` | — | — | `1` if speed exceeds threshold (25 m s⁻¹ for 50 km files; 35 m s⁻¹ for 75 km files); `0` = valid; for levels `02`/`03`, always `0` |
| `measurement_error` | — | — | `1` if `Maxcorr1 > Maxcorr2`; `0` = valid; for levels `02`/`03`, always `0` |

### NetCDF output variables

All gridded data variables have dimensions `(time, y, x)`. For the scenes file, each time layer corresponds to one scene pair. For the daily file, a single time layer mosaics all scene pairs using a last-write-wins strategy (scenes sorted by time before merge). The output grid is always the NSIDC 12.5 km polar stereographic grid (EPSG:3413) regardless of `config['epsg']`. The grid is cropped to the bounding box of valid observations with a 4-cell pad on each side.

| Variable | Dimensions | Type | Units | Description |
|----------|------------|------|-------|-------------|
| `sea_ice_speed` | (time, y, x) | float32 | m s⁻¹ | Gridded sea ice drift speed |
| `sea_ice_x_displacement` | (time, y, x) | float32 | m | X-component of ice displacement |
| `sea_ice_y_displacement` | (time, y, x) | float32 | m | Y-component of ice displacement |
| `direction_of_sea_ice_displacement` | (time, y, x) | float32 | degrees | Drift direction (forward azimuth) |
| `outlier_category` | (time, y, x) | int16 | — | Outlier classification; `−1` = inlier filter applied (level `03`); fill value = `−9` |
| `bearing_error` | (time, y, x) | int16 | — | Bearing/speed validity flag; `0` = valid, `1` = both zero; fill value = `−9` |
| `speed_error` | (time, y, x) | int16 | — | Speed threshold flag; `0` = valid, `1` = exceeded; fill value = `−9` |
| `measurement_error` | (time, y, x) | int16 | — | Cross-correlation quality flag; `0` = valid, `1` = failed; fill value = `−9` |
| `layer_id` *(coord)* | (time) | str | — | Full `scene_id` string for each time layer |
| `spatial_ref` | scalar | int32 | — | CRS container variable holding WKT/proj4 projection metadata |
| `time_bnds` | (time, nv=2) | float64 | s | CF time bounds in seconds since 2000-01-01 |
| `time` *(coord)* | (time) | float64 | s | Scene reference time in seconds since 2000-01-01 |
| `x` *(coord)* | (x) | float64 | m | x-coordinates of the 12.5 km polar stereographic grid |
| `y` *(coord)* | (y) | float64 | m | y-coordinates of the 12.5 km polar stereographic grid |

### GeoPackage output

For levels `00` and `02`, one layer per scene is written per day, named `drift_vectors_<sensor1>_<HH>_<MM>_<SS>_<sensor2>_<HH>_<MM>_<SS>`. For level `03`, a single combined `drift_vectors` layer contains all inlier vectors for the day. CRS: EPSG:`config['epsg']`. Geometry: `LineString` from `(X1, Y1)` to `(X2, Y2)`.

| Column | CRS / Reference | Units | Description |
|--------|----------------|-------|-------------|
| `scene_id` | — | — | Scene pair identifier |
| `sensor1`, `sensor2` | — | — | Satellite identifiers |
| `longitude_1`, `latitude_1` | EPSG:4326 | degrees | Start position |
| `longitude_2`, `latitude_2` | EPSG:4326 | degrees | End position |
| `X1`, `Y1`, `X2`, `Y2` | EPSG:`config['epsg']` | m | Projected start/end positions |
| `date_start`, `date_end` | — | — | Observation timestamps |
| `duration` | — | s | Observation duration |
| `sea_ice_x_displacement` | EPSG:`config['epsg']` | m | X displacement |
| `sea_ice_y_displacement` | EPSG:`config['epsg']` | m | Y displacement |
| `u`, `v` | EPSG:`config['epsg']` | m s⁻¹ | Velocity components |
| `sea_ice_speed` | geodesic | m s⁻¹ | Drift speed |
| `sea_ice_speed_kmdy` | geodesic | km/day | Drift speed in km/day |
| `direction_of_sea_ice_displacement` | geodesic | degrees | Drift direction |
| `distance`, `distance_geod` | geodesic | m | Euclidean and geodesic displacement distances |
| `outlier_category` | — | — | Outlier code; included for levels `00`, `02`, `03` |
| `geometry_type` | — | — | Literal `'line'` |

### Vector HTML and JSON output

One interactive HTML viewer file is produced per level/EPSG combination (levels `00` and `03`). It loads per-day JSON data files and renders SAR drift vectors and buoy drift vectors on an interactive Leaflet polar stereographic map.

**SAR drift JSON** (`data/si_velocity_<YYYYMMDD>.json`) and **Buoy drift JSON** (`data/buoy_velocity_<YYYYMMDD>.json`):

```json
{
  "date1": "YYYY-MM-DD",
  "date2": "YYYY-MM-DD",
  "count": <int>,
  "vectors": [[lon1, lat1, lon2, lat2, speed_kmdy, bearing], ...]
}
```

Buoy JSON files are written for all available dates in the UW IABP dataset on every run, ensuring delayed observations are captured regardless of when they arrive.

**Available dates JSON** (`data/available_dates.json`): sorted list of `YYYYMMDD` strings for all days that have a SAR drift JSON file.

---

## Outlier detection

The main outlier routine is `util.outlier_search`. It supports two methods:

- **Z-score** on drift speed and bearing, computed within a spatial neighborhood using `cKDTree.query_ball_point`
- **Mahalanobis distance** on displacement components `(dx, dy)` using `LedoitWolf` covariance estimation

Key design decisions:

- Neighbors are found **within each scene** (grouped by `File1`/`File2`)
- Outlier detection runs for up to `OUTLIER_PASSES` passes; on each pass the neighbor pool is restricted to current inliers (`outlier_category in ['00', '01']`), preventing flagged vectors from inflating local statistics
- Iteration stops early if the total inlier count stabilizes between passes
- `outlier_category` encodes **outlier type** (tens digit) and **statistical confidence** (units digit: `0` = below neighbor threshold, `1` = at or above):

| Code | Outlier Type |
|------|-------------|
| `−9` | Not computed (level `01`) |
| `−1` | Inlier — outlier filter already applied (level `03`) |
| `00` | No outlier (below neighbor threshold) |
| `01` | No outlier (at or above neighbor threshold) |
| `10`/`11` | Distance (speed) outlier |
| `20`/`21` | Bearing outlier |
| `30`/`31` | Mahalanobis distance outlier |
| `40`/`41` | Distance and bearing |
| `50`/`51` | Mahalanobis and distance |
| `60`/`61` | Mahalanobis and bearing |
| `70`/`71` | Mahalanobis, distance, and bearing |

---

## Output quality notes

- **75 km file preference:** For each 50 km gfilter file, the pipeline automatically checks for a corresponding 75 km file (`_0050000m_` → `_0075000m_`). If found, the 75 km file is read instead; the speed error threshold is adjusted accordingly (25 m s⁻¹ for 50 km files, 35 m s⁻¹ for 75 km files).
- **HH polarization filter:** Observations where either `File1` or `File2` does not use HH polarization are dropped before any processing. The count of dropped observations is logged.
- **Bearing and speed error flags:** For levels `00` and `01`, `bearing_error = 1` only when **both** bearing and speed are exactly zero simultaneously. For levels `02` and `03`, bad vectors are removed upstream so all surviving vectors receive flag values of `0`.
- **Reprocessing window:** `reprocess_days` in `config.json` automatically reprocesses the most recent N days on every run, ensuring outputs are updated when SAR or buoy source data is corrected or delayed.
- **Partial-day resume:** When `overwrite` is `false` and `reprocess_days` is `0`, each output type is checked independently. Days where only some outputs are missing are partially reprocessed.
- **float32 precision:** NetCDF variables are stored as `float32`. Cast to `float64` and re-round when exact decimal precision is required (e.g. in the notebook).

---

## Notebooks

### `sar_sea_ice_drift_netcdf_layer_viewer.ipynb`

An interactive Jupyter notebook for exploring and exporting individual time layers from the daily SAR sea-ice drift NetCDF product.

**What it does:**

- Opens a NetCDF file and displays a high-level dataset summary
- Lists all `layer_id` values (full `scene_id` strings) so a layer can be located by index or by searching for a target scene
- Computes per-variable statistics (shape, valid count, min/max/mean/median/std) for a selected layer, correctly handling the `_FillValue = −9` for int16 flag variables
- Exports a selected layer to a **GeoPackage** with an embedded QGIS QML style
- Renders a **quiver plot PNG** of drift vectors on a Cartopy basemap; projection is selected dynamically based on `epsg`

**Key parameters (set by the user):**

| Parameter | Description |
|-----------|-------------|
| `nc_path` | Path to the input NetCDF file |
| `selected_layer_index` | Integer index of the time layer to export/plot |
| `has_outliers` | `True` for levels `00`/`02` (colors arrows by outlier category); `False` for levels `01`/`03` (colors by displacement magnitude) |
| `epsg` | EPSG code of the projected CRS used in the NetCDF file (`3413` or `6931`) |

**Layer ID format:**

`layer_id` values are the full `scene_id` string, e.g.:
```
RCM1_SHUB_2024_10_14_05_18_19_0782198299_183.79E_75.03N_HH_C_RCM2_SHUB_2024_10_15_04_54_14_...
```

Uncomment the browse loop in the notebook to print all layer IDs if you need to find one by name.

**Outputs written to disk:**

| File | Location | Description |
|------|----------|-------------|
| `<layer_id>.gpkg` | `layer_to_gpkg/` | GeoPackage with drift line layer in EPSG:`epsg` and embedded QML style |

The PNG plot can be saved by right-clicking the inline image and choosing *Save Image As*.

---

## Quick checklist

1. Update `config.json` — set `sar_drift_directory`, `file_server`, `netcdf_template_file`, `netcdf_cdl_file`, `html_vector_template`, `html_index_template`, `meta_dir`, `buoy_dir`, `log_dir`, `output_dir`, and URL keys to match your environment
2. Ensure `beautifulsoup4`, `requests`, `scikit-learn`, and `urllib3` are installed (add to `environment.yml` and `requirements.txt` if not already present)
3. Run `python sar_drift_converter.py -c config.json`
4. Open the daily `.gpkg` in QGIS to verify vector placement and styling; use temporal control to step through scene layers
5. Serve `file_server` via localhost and open the `index.html` in a browser to verify the interactive map and buoy vectors
6. Validate `.nc` metadata and grid in the Jupyter notebook (both `_scenes_` and `_daily_` variants)

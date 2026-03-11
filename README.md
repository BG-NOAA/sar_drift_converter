# SAR Drift Converter & Outlier Tools

This repository converts **SAR sea‑ice drift “gfilter” text outputs** into GIS- and analysis-ready products:

- **Formatted CSV** (cleaned/consistent columns)
- **GeoPackage (`.gpkg`)** with start points, end points, and drift lines (EPSG:3411)
- **NetCDF (`.nc`)** on a regular grid with metadata populated from a **CDL template**
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
- `precision` (int): number of significant digits for nuermic values in data and computations

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

## Outputs

Given an input like:

```
RCM1_SHUB_2024_10_15_02_13_41_..._vel_1.01d_0050000m_0000500m.txt_0
```

you should expect (directories from `config.json`):

- formatted_data/<basename>.csv
- gpkg/<basename>.gpkg
- nc/<basename>.nc

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
are used as the pool whenrecomputing neighbors each iteration. This prevents already-flagged
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
- **“Pick up sticks” scenes:** If a scene has many invalid vectors (e.g., low correlation),
  it’s often best to discard that scene. Use `ignore_vector_threshold` and/or
  a "% correct" rule (e.g., `(Maxcorr2 > Maxcorr1)` fraction) upstream.

---

## Quick checklist

1. Update `config.json` paths (`sar_drift_directory`, output dirs, CDL template)
2. Run `python sar_drift_converter.py`
3. Open `.gpkg` in QGIS (EPSG:3411) to verify vector placement
4. Validate `.nc` metadata and grid
5. Enable outlier/plotting utilities as needed

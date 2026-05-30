# YSI Datasonde Data Plotter

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/hansen-matt/kor-datasonde-plotter/HEAD?urlpath=%2Fdoc%2Ftree%2FYSI_Datasonde_Plotter.ipynb)

A Jupyter notebook that reads CSV exports from [KOR Software](https://www.ysi.com/kor) (YSI EXO datasonde) and produces time-series plots for each detected dive. Each dive gets its own figure with five panels:

- **Depth** (ft)
- **Dissolved oxygen** (mg/L)
- **Temperature** (°C and °F)
- **Specific conductance** (µS/cm)
- **pH**

## Quickstart — no installation needed

Click the **launch binder** badge above. Once the environment loads, run all cells (**Run → Run All Cells**), upload your KOR CSV export, and click **Plot dives**.

## How to use

1. Export your data from KOR Software as a CSV file.
2. Open the notebook (via Binder or locally — see below).
3. **Run → Run All Cells** — the upload widget will appear.
4. Click **Upload CSV(s)** and select one or more KOR export files. Multiple files are processed separately.
5. Click **Plot dives**. A figure is generated for every dive detected in each file.

## Features

- **Automatic dive detection** — segments where the sonde descends below a configurable depth threshold are identified and merged if the gap between them is small.
- **Dual temperature axis** — each plot shows both °C and °F.
- **Summary statistics** — min, mean, max, and std for each parameter across every dive.
- **Interactive selector** — re-plot any individual dive and optionally save it as a PNG.
- **Multi-file support** — drop in an entire season's worth of exports at once.

## Adjustable settings

In the configuration cell (just below the upload widget) you can tune:

| Setting | Default | Description |
|---|---|---|
| `DIVE_THRESHOLD_FT` | 2 ft | Depth above which the sonde is considered at the surface |
| `MERGE_GAP_MIN` | 15 min | Merge dive segments separated by less than this |
| `PAD_MIN` | 10 min | Surface data to include before and after each dive |
| `MIN_MAX_DEPTH_FT` | 5 ft | Ignore excursions shallower than this (e.g. surface checks) |

After changing any setting, click **Run → Run All Cells** to replot.

## Running locally

```bash
pip install -r requirements.txt
jupyter notebook YSI_Datasonde_Plotter.ipynb
```

## Requirements

- Python 3.8+
- pandas, matplotlib, ipywidgets, jupyter

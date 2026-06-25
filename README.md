# YSI Datasonde Data Plotter

<p align="center">
  <a href="https://mybinder.org/v2/gh/hansen-matt/kor-datasonde-plotter/HEAD?urlpath=voila%2Frender%2FYSI_Datasonde_Plotter.ipynb">
    <img src="https://mybinder.org/badge_logo.svg" alt="Launch app" width="400">
  </a>
</p>

A Jupyter notebook that reads CSV exports from [KOR Software](https://www.ysi.com/kor) (YSI EXO datasonde) and produces time-series plots for each detected dive. Each dive gets its own figure with five panels:

- **Depth** (ft)
- **Dissolved oxygen** (mg/L)
- **Temperature** (°C and °F)
- **Specific conductance** (µS/cm)
- **pH**

## Quickstart — no installation needed

Click the **Launch app** badge above. The app opens automatically with the upload button ready — no code to run.

## How to use

1. Export your data from KOR Software as a CSV file.
2. Click the **Launch app** badge and wait for the environment to load (~1 minute).
3. Click **Upload CSV(s)** and select one or more KOR export files.
4. Click **Plot dives**.

To adjust detection settings or view the code, use the [notebook interface](https://mybinder.org/v2/gh/hansen-matt/kor-datasonde-plotter/HEAD?urlpath=%2Fdoc%2Ftree%2FYSI_Datasonde_Plotter.ipynb) instead.

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

After changing any setting, click **Run → Run All Cells** to replot. (Settings are only exposed in the notebook interface, not the app.)

## Running locally

```bash
pip install -r requirements.txt
jupyter notebook YSI_Datasonde_Plotter.ipynb
```

## Testing

`smoke_test.py` loads every CSV in `test_data/` through the notebook's own
loader (and renders each dive if matplotlib is installed), guarding against
Kor export format variations — encoding, column order, depth units, date
format — silently breaking the plotter. It exits non-zero if any file fails:

```bash
python smoke_test.py
```

## Requirements

- Python 3.8+
- pandas, matplotlib, ipywidgets, jupyter

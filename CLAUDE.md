# Instructions for Claude

A Jupyter notebook that plots dive profiles from YSI EXO datasonde CSV exports.
It is used two ways: as a Voilà web app on Binder by non-technical people, and
in batch from `~/Documents/datasonde/batch_plot.py` to render figures for
reports. Both run the *same* code — see "One source of truth" below.

## Layout

| Path | What it is |
|---|---|
| `YSI_Datasonde_Plotter.ipynb` | All the logic. The only place behaviour lives. |
| `smoke_test.py` | Lifts the notebook's definitions into a namespace and runs them over `test_data/`. Also the import hook every batch script uses. |
| `test_data/` | One CSV per Kor export dialect. Regression fixtures. |
| `README.md` | User-facing; Binder badge and instructions. |

## One source of truth

**Never reimplement notebook logic anywhere else.** `smoke_test.py` and the
batch scripts pull the notebook's own functions out at run time, so the web app
and the batch renderer cannot drift apart. If a helper is needed outside the
notebook, add it to the notebook and export it through `smoke_test.py`.

`smoke_test.load_notebook_namespace()` reads three cells:

- the settings cell — only names listed in `SETTINGS` are executed, so the
  upload widgets are skipped. **Add every new setting to that tuple**, or it
  will be missing at batch time while working fine in Jupyter.
- the loader cell — only names in `LOADER`, for the same reason.
- the plotting cell — executed whole; it is self-contained. Keep it that way.

## Editing the notebook

Edit it as JSON with a small Python script: load, find the cell by a substring
of its source, `assert` the old text appears exactly once, replace, dump with
`indent=1` and a trailing newline. That keeps the diff to the lines you meant to
change. Do not reformat the whole file.

## Verifying — required before claiming anything works

```bash
python smoke_test.py                              # all fixtures load, detect, render
cd ~/Documents/datasonde && python3 batch_plot.py # all 35 dives re-render
```

Then **look at a rendered PNG**. Layout bugs — collided labels, a black bar of
overlapping ticks, a title floating in dead space — are invisible to the tests
and have shipped here more than once. Read the image; do not assume.

For notebook-level changes also run:

```bash
jupyter nbconvert --to notebook --execute --output /tmp/x.ipynb YSI_Datasonde_Plotter.ipynb
```

Never report a fix you have not re-rendered and looked at.

## Domain facts that are easy to get wrong

- **Kor exports come in at least three header dialects**, differing in case,
  spacing and parenthesisation, plus 12- and 24-hour timestamps and a U+202F
  before AM/PM. Match headers on a normalised key, never on literal text.
  One file can hold several record blocks, each with its own header row.
- **The `Site Name` column is unusable** — empty or the placeholder `<site>`.
  The site comes from the filename, else the folder, else `SITE_OVERRIDES`.
- **Depth may be metres or feet** depending on the export.
- **Two depth thresholds exist and are not interchangeable.**
  `MIN_MAX_DEPTH_FT` decides which segments exist; `MIN_DIVE_DEPTH_FT` filters
  finished dives. Raising the first to filter dives moves dive boundaries and
  can split one dive in two.
- **Fixed step ladders run out.** SpCond spans 300 to 54,000 µS/cm across sites
  and depth reaches 251 ft. Any hard-coded step must have a computed fallback,
  or the axis becomes a solid block of labels.
- **Surface data is a different water mass.** Scales come from below
  `SCALE_MIN_DEPTH_FT`; traces are still drawn in full.

## Figure conventions

- Text wears neutral ink. The parameter colour goes on the trace and the left
  spine only — never on tick labels. Figures must read in greyscale.
- Validate any palette change with a colour-vision-deficiency checker rather
  than by eye; the previous palette had red↔green at ΔE 5.0 under deuteranopia.
- Grid and rules must survive downscaling. Dotted hairlines disappear first.
- Keep every figure at exactly `FIG_SIZE`; do not use `bbox_inches='tight'`,
  which sizes each one to its own labels.
- Out-of-range data auto-scales and is labelled "independent scale". Never clip
  data off a panel silently.

## Working style

- Say what you verified and what you did not. If a step was skipped, say so.
- When an instruction has a consequence the user may not intend — a filter that
  also moves dive boundaries, a shared scale that flattens every trace — do it,
  then tell them plainly.
- Commit to a branch, never `main`: Binder builds from `main`, so merging is
  the user's decision about when the live app changes.
- Commit messages explain *why*, including approaches that were tried and
  rejected. That history has been useful here.

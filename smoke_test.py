#!/usr/bin/env python3
"""Smoke test: load every CSV in test_data/ through the notebook's own loader.

This guards against Kor export format variations (encoding, column order,
depth units, date format) silently breaking the plotter. It pulls the real
`load_kor_csv` / `find_dives` / `plot_dive` out of YSI_Datasonde_Plotter.ipynb
so the test always exercises the shipped code rather than a drifting copy.

Run:   python smoke_test.py
Exits non-zero (and prints a traceback) if any file fails to load, detect
dives, or render. Intended for a quick manual check or CI.
"""
import ast
import glob
import json
import os
import sys
import traceback
import warnings

import pandas as pd

# The notebook suppresses these in its first cell; match that so plot_dive's
# tight_layout/twin-axis warnings don't clutter the test output.
warnings.filterwarnings('ignore')

HERE = os.path.dirname(os.path.abspath(__file__))
NOTEBOOK = os.path.join(HERE, 'YSI_Datasonde_Plotter.ipynb')
TEST_DIR = os.path.join(HERE, 'test_data')

# Names we need out of the notebook's settings cell — everything else there
# builds upload widgets, which cannot be constructed headless.
SETTINGS = ('DIVE_THRESHOLD_FT', 'MERGE_GAP_MIN', 'PAD_MIN', 'MIN_MAX_DEPTH_FT',
            'MIN_DIVE_DEPTH_FT', 'MIN_DURATION_MIN', 'SCALE_MIN_DEPTH_FT', 'FIG_SIZE', 'COLORS',
            'FIXED_DO_MGL', 'FIXED_TEMP_C', 'FIXED_SPCOND', 'FIXED_PH')
# Likewise for the loader cell, whose tail wires up the 'Plot dives' button.
LOADER = ('load_kor_csv', 'find_dives', 'format_duration', 'site_from_source', '_clean_site', '_norm_col', '_kor_header',
          'KOR_COL_MAP', 'KOR_DT_FORMATS')


def load_notebook_namespace():
    """Exec the loader/plotter definitions from the notebook into a namespace.

    Widget wiring and `display()`/`HTML` calls are stubbed so the cells can run
    headless, outside Jupyter.
    """
    nb = json.load(open(NOTEBOOK, encoding='utf-8'))
    cells = [''.join(c['source']) for c in nb['cells'] if c['cell_type'] == 'code']

    ns = {
        'pd': pd,
        'display': lambda *a, **k: None,
        'clear_output': lambda *a, **k: None,
        'HTML': lambda *a, **k: None,
    }
    import io as _io
    import re as _re
    import base64 as _base64
    import zipfile as _zipfile
    import numpy as _np
    ns.update(io=_io, re=_re, base64=_base64, zipfile=_zipfile, np=_np)

    # matplotlib is optional — without it we still load + detect dives, just skip
    # rendering. With it, we render headlessly to also exercise plot_dive.
    have_mpl = False
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates
        import matplotlib.ticker as mticker
        from matplotlib.gridspec import GridSpec
        ns.update(plt=plt, mdates=mdates, mticker=mticker, GridSpec=GridSpec)
        have_mpl = True
    except ImportError:
        pass

    def exec_names(src, names):
        """Exec only the top-level definitions and assignments named in `names`,
        leaving the widget wiring in the same cell alone. Parsed rather than
        matched line by line so multi-line values come through intact."""
        keep = []
        for n in ast.parse(src).body:
            if isinstance(n, ast.FunctionDef) and n.name in names:
                keep.append(n)
            elif isinstance(n, ast.Assign) and any(
                    isinstance(t, ast.Name) and t.id in names for t in n.targets):
                keep.append(n)
        exec(compile(ast.Module(body=keep, type_ignores=[]), '<nb>', 'exec'), ns)

    exec_names(next(c for c in cells if 'DIVE_THRESHOLD_FT' in c), set(SETTINGS))
    exec_names(next(c for c in cells if 'def load_kor_csv' in c), set(LOADER))
    # The plotting cell is self-contained, so run all of it — that way the test
    # exercises the real style setup, not just the functions.
    if have_mpl:
        exec(next(c for c in cells if 'def plot_dive' in c), ns)

    return ns, have_mpl


def main():
    ns, have_mpl = load_notebook_namespace()
    load_kor_csv = ns['load_kor_csv']
    find_dives = ns['find_dives']
    plot_dive = ns.get('plot_dive')

    files = sorted(glob.glob(os.path.join(TEST_DIR, '*.csv')))
    if not files:
        print(f'No CSV files found in {TEST_DIR}')
        return 1

    failures = 0
    for path in files:
        name = os.path.basename(path)
        try:
            df = load_kor_csv(open(path, 'rb').read())
            dives = find_dives(df)
            if plot_dive is not None:
                for i, ds in enumerate(dives, 1):
                    plot_dive(ds, idx=i, source_file=name)
            depth = df['depth_ft']
            print(f'OK    {name[:48]:48}  {len(df):>6,} rows  '
                  f'depth {depth.min():.1f}-{depth.max():.1f} ft  '
                  f'{len(dives)} dive(s)')
        except Exception:
            failures += 1
            print(f'FAIL  {name}')
            traceback.print_exc()

    print()
    if failures:
        print(f'{failures} of {len(files)} file(s) failed.')
        return 1
    note = '' if have_mpl else '  (matplotlib not installed — rendering skipped)'
    print(f'All {len(files)} file(s) loaded and detected dives.{note}')
    return 0


if __name__ == '__main__':
    sys.exit(main())

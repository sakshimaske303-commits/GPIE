"""Re-run every estimate, table and figure in the GPIE research paper, in order.

I run this from the repository root:

    python reproduce_paper.py                 # run all steps whose inputs are present
    python reproduce_paper.py --check         # only list what can run and what is missing
    python reproduce_paper.py --from 4        # start at step 4
    python reproduce_paper.py --compare DIR   # compare data/*.json with an earlier copy in DIR

The steps start from the processed data, so they need no accounts. The pixel-level steps
also need the monthly 0.1 degree NO2 grid (about 77 MB, not stored in the repository) and the
GADM boundaries; the script says which download script makes each missing file.
"""

import argparse
import glob
import json
import math
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.abspath(__file__))

GRID = "data/earth_observation/no2/gridded/no2_grid_monthly.npz"
NUTS = "data/earth_observation/boundaries/raw/NUTS_LEVL_0_2024_4326.geojson"
GADM = [f"data/earth_observation/boundaries/raw/gadm41_{c}_0.json" for c in ("GBR", "NOR", "CHE")]
PANEL = "data/master_dataset_control.csv"

# where each missing input comes from
MAKES = {
    GRID: "src/download_no2_gridded.py (needs a free Sentinel Hub account)",
    NUTS: "src/download_nuts.py",
    PANEL: "step 1 of this script",
    "data/stress_tests.json": "step 4 of this script",
    "data/earth_observation/economy/final/gdp_per_capita_real.csv": "src/download_gdp_real.py",
    "data/eea_station_monthly.csv": "airbase download into data/eea_no2/, then src/validate_eea_stations.py",
}
for g in GADM:
    MAKES[g] = "src/download_gadm.py"

BOUNDS = [NUTS] + GADM

# (label, script, inputs it needs, what it produces in the paper)
STEPS = [
    ("Country panel: NO2, weather and GDP for 36 countries x 72 months",
     "master_merge_control.py",
     ["data/earth_observation/no2/final/no2_stats_monthly_mean_36.json"],
     "data/master_dataset_control.csv"),
    ("Country-level DiD and its specifications",
     "causal_inference_identification_checks.py",
     [PANEL, "data/covid/oxcgrt_stringency_national.csv", "data/era5_wind_blh_country_monthly.csv"],
     "Table 2, Sections 5.1-5.3"),
    ("Pixel level: change by starting level, matched DiD",
     "analyse_no2_grid_baseline.py",
     [PANEL, GRID] + BOUNDS,
     "Tables 3-4, Figures 4-5"),
    ("Random assignment, regional contrasts, where NO2 fell",
     "causal_inference_stress_tests.py",
     [PANEL, GRID] + BOUNDS,
     "Figure 3, Table 5, Figure 6"),
    ("Additional checks on the matched model",
     "causal_inference_additional_checks.py",
     [PANEL, GRID] + BOUNDS,
     "Table 4 (blocks, COVID exclusion)"),
    ("Positive control: does the model find a known reduction?",
     "causal_inference_positive_control.py",
     [PANEL, GRID] + BOUNDS,
     "Table 6, Figure 7"),
    ("Real GDP per capita in place of nominal GDP",
     "causal_inference_real_gdp.py",
     [PANEL, GRID, "data/earth_observation/economy/final/gdp_per_capita_real.csv"] + BOUNDS,
     "Real GDP rows of Tables 2 and 4"),
    ("Ground stations: does the satellite agree with the ground?",
     "validate_eea_stations.py",
     [PANEL, GRID, "data/eea_station_monthly.csv"] + BOUNDS,
     "Table 7, Section 5.7"),
    ("Spatial autocorrelation of the residuals",
     "spatial_autocorrelation.py",
     [PANEL] + BOUNDS,
     "Moran's I, Section 5.1"),
    ("Figure 1: study design map",
     "map_control_group_highlight.py",
     BOUNDS,
     "Figure 1"),
    ("Figure 2: blocks of months around the law",
     "plot_block_event_study.py",
     ["data/stress_tests.json"],
     "Figure 2"),
]


def missing(inputs):
    return [p for p in inputs if not os.path.exists(os.path.join(ROOT, p))]


def check():
    print("What can run now:\n")
    for i, (label, script, inputs, out) in enumerate(STEPS, 1):
        miss = missing(inputs)
        print(f"  [{i:2d}] {'ready  ' if not miss else 'missing'}  {label}")
        for m in miss:
            print(f"               needs {m}\n               from  {MAKES.get(m, 'see README')}")


def run(start):
    os.chdir(ROOT)
    done, skipped = [], []
    t0 = time.time()
    for i, (label, script, inputs, out) in enumerate(STEPS, 1):
        if i < start:
            continue
        print(f"\n[{i}/{len(STEPS)}] {label}  ->  {out}")
        miss = missing(inputs)
        if miss:
            print("   skipped, missing: " + ", ".join(miss))
            skipped.append(i)
            continue
        t = time.time()
        r = subprocess.run([sys.executable, os.path.join("src", script)])
        if r.returncode != 0:
            print(f"\nStep {i} ({script}) stopped with an error. Nothing after it was run.")
            sys.exit(r.returncode)
        print(f"   done in {time.time() - t:.0f} s")
        done.append(i)
    print(f"\nFinished in {(time.time() - t0) / 60:.1f} min. Ran steps {done or 'none'}; skipped {skipped or 'none'}.")


def flatten(x, prefix=""):
    if isinstance(x, dict):
        for k, v in x.items():
            yield from flatten(v, f"{prefix}.{k}" if prefix else str(k))
    elif isinstance(x, list):
        for k, v in enumerate(x):
            yield from flatten(v, f"{prefix}[{k}]")
    else:
        yield prefix, x


def compare(old_dir, tol=1e-6):
    os.chdir(ROOT)
    files = sorted(glob.glob(os.path.join(old_dir, "*.json")))
    if not files:
        sys.exit(f"No .json files in {old_dir}")
    total = 0
    for f in files:
        name = os.path.basename(f)
        new = os.path.join("data", name)
        if not os.path.exists(new):
            print(f"{name}: not produced in this run")
            continue
        a = dict(flatten(json.load(open(f, encoding="utf-8"))))
        b = dict(flatten(json.load(open(new, encoding="utf-8"))))
        diffs = []
        for k in sorted(set(a) | set(b)):
            x, y = a.get(k), b.get(k)
            if isinstance(x, (int, float)) and isinstance(y, (int, float)) and not isinstance(x, bool):
                if isinstance(x, float) and math.isnan(x) and isinstance(y, float) and math.isnan(y):
                    continue
                if abs(x - y) > tol * max(1.0, abs(x), abs(y)):
                    diffs.append(f"    {k}: {x} -> {y}")
            elif x != y:
                diffs.append(f"    {k}: {str(x)[:60]} -> {str(y)[:60]}")
        total += len(diffs)
        print(f"{name}: {'same' if not diffs else f'{len(diffs)} differences'}")
        for d in diffs[:15]:
            print(d)
        if len(diffs) > 15:
            print(f"    ... and {len(diffs) - 15} more")
    print(f"\n{'All numbers are the same.' if total == 0 else f'{total} differences in total.'}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="only list which steps can run")
    ap.add_argument("--from", dest="start", type=int, default=1, help="first step to run")
    ap.add_argument("--compare", metavar="DIR", help="compare data/*.json with the files in DIR")
    args = ap.parse_args()
    if args.compare:
        compare(args.compare)
    elif args.check:
        check()
    else:
        run(args.start)

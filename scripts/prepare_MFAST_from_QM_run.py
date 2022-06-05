# -*- coding: utf-8 -*-
"""
Example script for converting the outputs of a QuakeMigrate run to inputs for
MFAST.

:copyright:
    2021--2022, AnisotropIO developers.
:license:
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.html)

"""

import pathlib

import pandas as pd

from anisotropio.io import Archive, read_stations
import anisotropio.translators as translate

# ------------------------ EDIT THIS SECTION ------------------------
base_path = pathlib.Path(
    "/path/to/quakemigrate/examples/Volcanotectonic_Iceland"
)
run_dir = base_path / "outputs/runs/example_run"
stations = read_stations(base_path / "inputs/iceland_stations.txt")
archive = Archive(
    archive_path="/path/to/data/ARCHIVE",
    stations=stations,
    archive_format="YEAR/JD/*_STATION_*"
)
run_subname = ""
out_dir = None
# -------------------------------------------------------------------

# --- Parse all events files into DataFrame ---
events_dir = run_dir / "locate" / run_subname / "events"
events_df = [pd.read_csv(fname) for fname in events_dir.glob("*.event")]
events = pd.concat(events_df)

# ------------- APPLY ANY EVENT FILTERING YOU WANT HERE -------------
# For example, you might wish to filter for incidence angle,
# geographical region, timing, etc... Optionally, you can 
# do all the filtering elsewhere, and skip the reading from
# the raw QM outputs as is done above.

# --- Prepare MFAST inputs ---
translate.qm2mfast(
    events,
    run_dir,
    archive,
    stations,
    out_dir=out_dir,
    run_subname=run_subname
)

# -*- coding: utf-8 -*-
"""
Module providing utility functions for converting QuakeMigrate outputs to the
inputs for various shear-wave splitting codes.

:copyright:
    2021--2022, AnisotropIO developers.
:license:
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.html)

"""

import pathlib

import obspy
import pandas as pd

import anisotropio.composers as compose


def qm2mfast(events, run_dir, archive, stations, out_dir=None, run_subname=""):
    """
    Reads the .picks outputs from a QuakeMigrate run, accesses an archive of
    waveform data, and writes to .sac files (prepared for MFAST).

    Parameters
    ----------
    events : `pandas.DatFrame` object
        Contains information about event hypocentres and origin times.
    run_dir : `pathlib.Path` object
        Directory containing the target QuakeMigrate run outputs.
    archive : `anisotropIO.io.Archive` object
        Details the structure and location of a data archive and provides
        methods for reading data from file.
    stations : `pandas.DataFrame` object
        Station information.
        Columns: "Latitude", "Longitude", "Elevation", "Name"
    out_dir : str, optional
        Path to location to which to write the SAC files.
    run_subname : str, optional
        Optional sub-name used in QuakeMigrate.

    """

    locate_dir = pathlib.Path(run_dir) / "locate" / run_subname

    out_dir = pathlib.Path.cwd() if out_dir is None else pathlib.Path(out_dir)

    for _, event in events.iterrows():
        picks = _read_event_picks(event["EventID"], locate_dir)
        if picks is None:
            print("Something wrong with reading picks")
            continue

        # --- Filter for automatic S picks ---
        picks = picks[
            (picks["Phase"] == "S") & (picks["PickTime"].astype(str) != "-1")
        ]
        if picks.empty:
            print("No available S picks!")
            continue

        # --- Convert picks to UTCDateTime objects ---
        picks["PickTime"] = picks["PickTime"].apply(obspy.UTCDateTime)

        # --- Find min/max pick times and use to query data from archive ---
        min_time, max_time = picks["PickTime"].min(), picks["PickTime"].max()
        data = archive.read_waveform_data(
            min_time - 15,
            max_time + 15,
            pre_pad=1.5,
            post_pad=1.5
        )
        stream = data.waveforms

        # --- For each pick, slice relevant window of data and write SAC ---
        for _, pick in picks.iterrows():
            station = stations[stations["Name"] == pick.Station].squeeze()

            tmp_stream = stream.select(station=pick.Station)
            tmp_stream = tmp_stream.slice(
                starttime=pick.PickTime - 15,
                endtime=pick.PickTime + 15
            )

            compose.mfast_sac_files(tmp_stream, event, station, out_dir)


def _read_event_picks(event_uid, locate_dir):
    """
    Find and read the QuakeMigrate .picks file for a given event.

    Parameters
    ----------
    event_uid : str
        Unique event identifier.
    locate_dir : `pathlib.Path` object
        Path to locate directory containing the "picks" directory.

    Returns
    -------
    picks : `pandas.DataFrame` object
        Contains pick information for each event-station pair.

    """

    pick_file = locate_dir / f"picks/{event_uid}"
    if pick_file.with_suffix(".picks").is_file():
        picks = pd.read_csv(pick_file.with_suffix(".picks"))
    else:
        # Consider raising an error here?
        return None

    return picks

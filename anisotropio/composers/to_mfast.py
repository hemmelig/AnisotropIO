# -*- coding: utf-8 -*-
"""
This module provides functions to compose the inputs for MFAST - SAC waveform files,
with correctly populated headers, are prepared from ObsPy Streams and either an ObsPy
Event object, or simply a dataframe containing the event information.

:copyright:
    2023, AnisotropIO developers.
:license:
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.html)

"""

import obspy
from obspy.core import AttribDict
from obspy.geodetics import gps2dist_azimuth


cmpaz = {"N": 0, "Z": 0, "E": 90}
cmpinc = {"N": 90, "Z": 0, "E": 90}


def mfast_sac_files(stream, event_info, station, output_path):
    """
    Function to create the SAC file.

    Parameters
    ----------
    stream : `obspy.Stream` object
        Waveform data to be sliced.
    event_info : `pandas.Series` object
        Contains information about event hypocentre and origin time.
    station : `pandas.Series` object
        Series containing station information.
    output_path : `pathlib.Path` object
        Location to save the SAC file.

    """

    # --- Build the event information header ---
    event_header = AttribDict()
    event_header.evla = event_info.Y
    event_header.evlo = event_info.X
    event_header.evdp = event_info.Z
    eventid = str(event_info.EventID)

    # --- Build the station information header ---
    station_header = AttribDict()
    station_header.stla = str(station.Latitude)
    station_header.stlo = str(station.Longitude)
    station_header.stel = str(station.Elevation)

    # Calculate the distance and azimuth between event and station
    dist, az, _ = gps2dist_azimuth(
        event_header.evla,
        event_header.evlo,
        station.Latitude,
        station.Longitude
    )
    station_header.dist = str(dist / 1000.)
    station_header.az = str(az)

    # --- Build the pick information header ---
    pick_header = AttribDict()
    pick_header.t5 = "15.0"
    pick_header.kt5 = "1"  # Pick error - incorporate uncertainty from QM picks?
    pick_header.o = obspy.UTCDateTime(event_info.DT)
    pick_header.a = "0.0"  # On review, it seems like this should be the P-pick time

    fname = eventid + ".{}.{}"
    output_path = output_path / eventid / station["Name"]
    output_path.mkdir(parents=True, exist_ok=True)

    for component in "ZNE":
        trace = stream.select(component=component)[0]

        # Write out to SAC file, then read in again to fill header
        name = fname.format(station["Name"], component.lower())
        name = str(output_path / name)
        trace.write(name, format="SAC")
        trace = obspy.read(name)[0]

        sac_header = AttribDict()
        sac_header.cmpaz = str(cmpaz[component])
        sac_header.cmpinc = str(cmpinc[component])
        sac_header.kcmpnm = f"HH{component}"
        sac_header.update(event_header)
        sac_header.update(station_header)
        sac_header.update(pick_header)
        trace.stats.sac.update(sac_header)

        trace.write(name, format="SAC")

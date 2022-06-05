# -*- coding: utf-8 -*-
"""
Module to handle input/output for AnisotropIO.

:copyright:
    2021--2022, AnisotropIO developers.
:license:
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.html)

"""

import pandas as pd
from obspy import read_inventory

import anisotropio.utils.errors as errors


def read_stations(station_file, **kwargs):
    """
    Reads station information from file.

    Parameters
    ----------
    station_file : str
        Path to station file.
        File format (header line is REQUIRED, case sensitive, any order):
            Latitude, Longitude, Elevation (units matching LUT grid projection;
            either metres or kilometres; positive upwards), Name
    kwargs : dict
        Passthrough for `pandas.read_csv` kwargs.

    Returns
    -------
    stn_data : `pandas.DataFrame` object
        Columns: "Latitude", "Longitude", "Elevation", "Name"

    Raises
    ------
    InvalidStationFileHeader
        Raised if the input file is missing required entries in the header.

    """

    stn_data = pd.read_csv(station_file, **kwargs)

    if ("Latitude" or "Longitude" or "Elevation" or "Name") \
       not in stn_data.columns:
        raise errors.InvalidStationFileHeader

    stn_data["Elevation"] = stn_data["Elevation"].apply(lambda x: -1*x)

    # Ensure station names are strings
    stn_data = stn_data.astype({"Name": "str"})

    return stn_data


def read_response_inv(response_file, sac_pz_format=False):
    """
    Reads response information from file, returning it as a `obspy.Inventory`
    object.

    Parameters
    ----------
    response_file : str
        Path to response file.
        Please see the `obspy.read_inventory()` documentation for a full list
        of supported file formats. This includes a dataless.seed volume, a
        concatenated series of RESP files or a stationXML file.
    sac_pz_format : bool, optional
        Toggle to indicate that response information is being provided in SAC
        Pole-Zero files. NOTE: not yet supported.

    Returns
    -------
    response_inv : `obspy.Inventory` object
        ObsPy response inventory.

    Raises
    ------
    NotImplementedError
        If the user selects `sac_pz_format=True`.
    TypeError
        If the user provides a response file that is not readable by ObsPy.

    """

    if sac_pz_format:
        raise NotImplementedError(
            "SAC_PZ is not supported. Contact the AnisotropIO developers."
        )
    else:
        try:
            response_inv = read_inventory(response_file)
        except TypeError as e:
            msg = (f"Response file not readable by ObsPy: {e}\n"
                   "Please consult the ObsPy documentation.")
            raise TypeError(msg)

    return response_inv

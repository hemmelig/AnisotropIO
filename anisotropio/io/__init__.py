# -*- coding: utf-8 -*-
"""
The :mod:`anisotropio.io` module handles the various input/output operations
performed by AnisotropIO. This includes:

    * Reading waveform data - The submodule data.py can handle any waveform \
      data archive with a regular directory structure. It also provides \
      functions for checking data quality and removing/simulating instrument \
      reponse.
    * Reading station files and instrument response inventories.

:copyright:
    2021--2022, AnisotropIO developers.
:license:
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.html)

"""

from .data import Archive  # NOQA
from .core import (read_response_inv, read_stations)  # NOQA

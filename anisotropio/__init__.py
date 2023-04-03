# -*- coding: utf-8 -*-
"""
AnisotropIO—a Python backend toolkit for parsing, composing, and translating between
inputs/outputs for various shear-wave splitting analysis codes.

:copyright:
    2023, AnisotropIO developers.
:license:
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.html)

"""

import importlib.metadata


__all__ = ["composers", "io", "parsers", "translators", "utils"]

__version__ = importlib.metadata.version("anisotropy")

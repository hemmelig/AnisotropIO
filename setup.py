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

import sys

from setuptools import setup


if __name__ == "__main__":
    # clean --all does not remove extensions automatically
    if "clean" in sys.argv and "--all" in sys.argv:
        import pathlib
        import shutil

        # Delete complete build directory
        path = pathlib.Path.cwd() / "build"
        shutil.rmtree(str(path), ignore_errors=True)
    else:
        setup()

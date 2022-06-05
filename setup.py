# -*- coding: utf-8 -*-
"""
AnisotropIO - a Python backend toolkit for parsing, composing, and translating
between inputs/outputs for various shear-wave splitting analysis codes.

:copyright:
    2021--2022, AnisotropIO developers.
:license:
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.html)

"""

import os
import pathlib
import shutil
import sys

from setuptools import find_packages, setup


# The minimum python version which can be used to run AnisotropIO
MIN_PYTHON_VERSION = (3, 7)

# Fail fast if the user is on an unsupported version of Python.
if sys.version_info < MIN_PYTHON_VERSION:
    msg = (f"AnisotropIO requires python version >= {MIN_PYTHON_VERSION}"
           f" you are using python version {sys.version_info}")
    print(msg, file=sys.stderr)
    sys.exit(1)

# Check if we are on RTD and don't build extensions if we are.
READ_THE_DOCS = os.environ.get("READTHEDOCS", None) == "True"

# Directory of the current file
SETUP_DIRECTORY = pathlib.Path.cwd()
DOCSTRING = __doc__.split("\n")

INSTALL_REQUIRES = [
    "numpy",
    "obspy>=1.2",
    "pandas"
]

if READ_THE_DOCS:
    EXTRAS_REQUIRES = {
        "docs": [
            "Sphinx >= 1.8.1",
            "docutils"
        ]
    }
else:
    EXTRAS_REQUIRES = {
        
    }

KEYWORDS = [
    "array", "anisotropy", "seismic", "seismology", "earthquake", "splitting",
    "modelling", "ObsPy", "waveform", "seismic anisotropy", "processing"
]


def setup_package():
    """Setup package"""

    setup_args = {
        "name": "anisotropio",
        "description": " ".join(DOCSTRING[1:3]),
        "long_description": "\n".join(DOCSTRING[4:]),
        "url": "https://github.com/hemmelig/AnisotropIO",
        "author": "The AnisotropIO Development Team",
        "author_email": "conor.bacon@esc.cam.ac.uk",
        "license": "GNU General Public License, Version 3 (GPLv3)",
        "classifiers": [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Science/Research",
            "Topic :: Scientific/Engineering",
            "Natural Language :: English",
            "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
            "Operating System :: OS Independent",
            "Programming Language :: Python",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
        ],
        "keywords": KEYWORDS,
        "install_requires": INSTALL_REQUIRES,
        "extras_require": EXTRAS_REQUIRES,
        "zip_safe": False,
        "packages": find_packages(),
    }

    shutil.rmtree(str(SETUP_DIRECTORY / "build"), ignore_errors=True)

    setup(**setup_args)


if __name__ == "__main__":
    # clean --all does not remove extensions automatically
    if "clean" in sys.argv and "--all" in sys.argv:
        # Delete complete build directory
        path = SETUP_DIRECTORY / "build"
        shutil.rmtree(str(path), ignore_errors=True)

    else:
        setup_package()

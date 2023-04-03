# -*- coding: utf-8 -*-
"""
Module that supplies various utility functions and classes.

:copyright:
    2023, AnisotropIO developers.
:license:
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.html)

"""

import logging
import sys
import time
from datetime import datetime
from functools import wraps
from itertools import tee


log_spacer = "="*110


def make_directories(run, subdir=None):
    """
    Make run directory, and optionally make subdirectories within it.

    Parameters
    ----------
    run : `pathlib.Path` object
        Location of parent output directory, named by run name.
    subdir : str, optional
        subdir to make beneath the run level.

    """

    run.mkdir(exist_ok=True)

    if subdir:
        new_dir = run / subdir
        new_dir.mkdir(exist_ok=True, parents=True)


def logger(logstem, log, loglevel="info"):
    """
    Simple logger that will output to both a log file and stdout.

    Parameters
    ----------
    logstem : str
        Filestem for log file.
    log : bool
        Toggle for logging - default is to only print information to stdout.
        If True, will also create a log file.
    loglevel : str, optional
        Toggle for logging level - default is to print only "info" messages to
        log. To print more detailed "debug" messages, set to "debug".

    """

    level = logging.DEBUG if loglevel == "debug" else logging.INFO

    if log:
        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        logfile = logstem.parent / f"{logstem.name}_{now}"
        logfile.parent.mkdir(exist_ok=True, parents=True)
        handlers = [logging.FileHandler(str(logfile.with_suffix(".log"))),
                    logging.StreamHandler(sys.stdout)]
    else:
        handlers = [logging.StreamHandler(sys.stdout)]

    logging.basicConfig(level=level,
                        format="%(message)s",
                        handlers=handlers)
                        # format="%(asctime)s [%(levelname)s] %(message)s",

def time2sample(time, sampling_rate):
    """
    Utility function to convert from seconds and sampling rate to number of
    samples.

    Parameters
    ----------
    time : float
        Time to convert
    sampling_rate : int
        Sampling rate of input data/sampling rate at which to compute
        the coalescence function.

    Returns
    -------
    out : int
        Time that correpsonds to an integer number of samples at a specific
        sampling rate.

    """

    return int(round(time*int(sampling_rate)))


def pairwise(iterable):
    """Utility to iterate over an iterable pairwise."""

    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


def timeit(*args_, **kwargs_):
    """Function wrapper that measures the time elapsed during its execution."""
    def inner_function(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            ts = time.time()
            result = func(*args, **kwargs)
            msg = " "*21 + f"Elapsed time: {time.time() - ts:6f} seconds."
            try:
                if args_[0] == "info":
                    logging.info(msg)
            except IndexError:
                logging.debug(msg)
            return result
        return wrapper
    return inner_function

# -*- coding: utf-8 -*-
"""
Module that supplies various utility functions for manipulating waveform data.

:copyright:
    2023, AnisotropIO developers.
:license:
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.html)

"""

import logging

import numpy as np
from obspy import Trace

from anisotropio.utils import errors


def azinc2vec(ψ, θ):
    """
    Return a 3-vector with the direction defined by (ψ, θ)

    Parameters
    ----------
    ψ : float
        Azimuth from x1 towards x2. Units of degrees.
    θ : float
        Inclination from the x1-x2 plane towards x3. Units of degrees.

    Returns
    -------
    x : array
        Vector pointing along (ψ, θ).

    """

    ψ, θ = np.deg2rad([ψ, θ])

    return np.array([np.cos(ψ)*np.cos(θ), -np.sin(ψ)*np.cos(θ), np.sin(θ)])


def rotate2xy(vector, azimuth, inclination):
    """
    Rotate a 3-vector into the x-y plane.

    Parameters
    ----------
    azimuth : list of float or float
        Azimuth, ψ, from x1 towards x2, in degrees.
    inclination : list of float or float
        Inclination, θ, from the x1-x2 plane towards x3, in degrees.

    Returns
    -------
    x : array
        Vector within the x-y plane.

    """

    ψ, θ = np.deg2rad([azimuth, inclination])

    r1 = np.array([[ np.cos(ψ), np.sin(ψ), 0],
                   [-np.sin(ψ), np.cos(ψ), 0],
                   [         0,         0, 1]])
    r2 = np.array([[np.cos(θ), 0, -np.sin(θ)],
                   [        0, 1,          0],
                   [np.sin(θ), 0,  np.cos(θ)]])

    return np.dot(np.dot(vector, r1), r2)


def trim2sample(time, sampling_rate):
    """
    Utility function to ensure time padding results in a time that is an
    integer number of samples.

    Parameters
    ----------
    time : float
        Time to trim.
    sampling_rate : int
        Sampling rate of input data/sampling rate at which to compute
        the coalescence function.

    Returns
    -------
    out : int
        Time that corresponds to an integer number of samples at a specific
        sampling rate.

    """

    return int(np.ceil(time * sampling_rate) / sampling_rate * 1000) / 1000


def wa_response(convert='DIS2DIS', obspy_def=True):
    """
    Generate a Wood Anderson response dictionary.

    Parameters
    ----------
    convert : {'DIS2DIS', 'VEL2VEL', ‘VEL2DIS'}
        Type of output to convert between; determines the number of complex
        zeros used.
    obspy_def : bool, optional
        Use the ObsPy definition of the Wood Anderson response (Default).
        Otherwise, use the IRIS/SAC definition.

    Returns
    -------
    WOODANDERSON : dict
        Poles, zeros, sensitivity and gain of the Wood-Anderson torsion
        seismograph.

    """

    if obspy_def:
        # Create Wood-Anderson response - ObsPy values
        woodanderson = {"poles": [-6.283185 - 4.712j,
                                  -6.283185 + 4.712j],
                        "zeros": [0j],
                        "sensitivity": 2080,
                        "gain": 1.}
    else:
        # Create Wood Anderson response - different to the ObsPy values
        # http://www.iris.washington.edu/pipermail/sac-help/2013-March/001430.html
        woodanderson = {"poles": [-5.49779 + 5.60886j,
                                  -5.49779 - 5.60886j],
                        "zeros": [0j],
                        "sensitivity": 2080,
                        "gain": 1.}

    if convert in ('DIS2DIS', 'VEL2VEL'):
        # Add an extra zero to go from disp to disp or vel to vel.
        woodanderson['zeros'].extend([0j])

    return woodanderson


def shift_to_sample(stream, interpolate=False):
    """
    Check whether any data in an `obspy.Stream` object is "off-sample" - i.e.
    the data timestamps are *not* an integer number of samples after midnight.
    If so, shift data to be "on-sample".

    This can either be done by shifting the timestamps by a sub-sample time
    interval, or interpolating the trace to the "on-sample" timestamps. The
    latter has the benefit that it will not affect the timing of the data, but
    will require additional computation time and some inevitable edge effects -
    though for onset calculation these should be contained within the pad
    windows. If you are using a sampling rate < 1 Hz, contact the AnisotropIO
    developers.

    Parameters
    ----------
    stream : `obspy.Stream` object
        Contains list of `obspy.Trace` objects for which to check the timing.
    interpolate : bool, optional
        Whether to interpolate the data to correct the "off-sample" timing.
        Otherwise, the metadata will simply be altered to shift the timestamps
        "on-sample"; this will lead to a sub-sample timing offset.

    Returns
    -------
    stream : `obspy.Stream` object
        Waveform data with all timestamps "on-sample".

    """

    # work on a copy
    stream = stream.copy()

    for tr in stream:
        # Check if microsecond is divisible by sampling rate; only guaranteed
        # to work for sampling rates of 1 Hz or less
        delta = tr.stats.starttime.microsecond \
            % (1e6 / tr.stats.sampling_rate)
        if delta == 0:
            if tr.stats.sampling_rate < 1.:
                logging.warning(f"Trace\n\t{tr}\nhas a sampling rate less than"
                                " 1 Hz, so off-sample data might not be "
                                "corrected!")
            continue
        else:
            # Calculate time shift to closest "on-sample" timestamp
            time_shift = round(delta / 1e6 * tr.stats.sampling_rate) \
                / tr.stats.sampling_rate - delta / 1e6
            if not interpolate:
                logging.info(f"Trace\n\t{tr}\nhas off-sample data. Applying "
                             f"{time_shift:+f} s shift to timing.")
                tr.stats.starttime += time_shift
                logging.debug(f"Shifted trace: {tr}")
            else:
                logging.info(f"Trace\n\t{tr}\nhas off-sample data. "
                             f"Interpolating to apply a {time_shift:+f} s "
                             "shift to timing.")
                # Interpolate can only map between values contained within the
                # original array. For negative time shift, shift by one sample
                # so new starttime is within original array, and add constant
                # value pad after interpolation.
                new_starttime = tr.stats.starttime + time_shift
                if time_shift < 0.:
                    new_starttime += tr.stats.delta
                tr.interpolate(sampling_rate=tr.stats.sampling_rate,
                               method="lanczos", a=20, starttime=new_starttime)
                # Add constant-value pad at end if time_shift is positive,
                # (last sample is dropped when interpolating for positive time
                # shifts), else at start. If adding at start, also adjust start
                # time.
                if time_shift > 0.:
                    tr.data = np.append(tr.data, tr.data[-1])
                else:
                    tr.data = np.append(tr.data[0], tr.data)
                    tr.stats.starttime -= tr.stats.delta
                logging.debug(f"Interpolated tr:\n\t{tr}")

    return stream


def resample(stream, sampling_rate, resample, upfactor, starttime, endtime):
    """
    Resample data in an `obspy.Stream` object to the specified sampling rate.

    By default, this function will only perform decimation of the data. If
    necessary, and if the user specifies `resample = True` and an upfactor
    to upsample by `upfactor = int`, data can also be upsampled and then,
    if necessary, subsequently decimated to achieve the desired sampling
    rate.

    For example, for raw input data sampled at a mix of 40, 50 and 100 Hz,
    to achieve a unified sampling rate of 50 Hz, the user would have to
    specify an upfactor of 5; 40 Hz x 5 = 200 Hz, which can then be
    decimated to 50 Hz.

    NOTE: assumes any data with off-sample timing has been corrected with
    :func:`~anisotropio.utils.trace.shift_to_sample`. If not, the resulting
    traces may not all contain the correct number of samples.

    NOTE: data will be detrended and a cosine taper applied before
    decimation, in order to avoid edge effects when applying the lowpass
    filter.

    Parameters
    ----------
    stream : `obspy.Stream` object
        Contains list of `obspy.Trace` objects to be decimated / resampled.
    resample : bool
        If true, perform resampling of data which cannot be decimated
        directly to the desired sampling rate.
    upfactor : int or None
        Factor by which to upsample the data to enable it to be decimated
        to the desired sampling rate, e.g. 40Hz -> 50Hz requires
        upfactor = 5.

    Returns
    -------
    stream : `obspy.Stream` object
        Contains list of resampled `obspy.Trace` objects at the chosen
        sampling rate `sr`.

    """

    # Work on a copy of the stream
    stream = stream.copy()

    for trace in stream:
        trace_sampling_rate = trace.stats.sampling_rate
        if sampling_rate != trace_sampling_rate:
            if (trace_sampling_rate % sampling_rate) == 0:
                stream.remove(trace)
                trace = decimate(trace, sampling_rate)
                stream += trace
            elif resample and upfactor is not None:
                # Check the upsampled sampling rate can be decimated to sr
                if int(trace_sampling_rate * upfactor) % sampling_rate != 0:
                    raise errors.BadUpfactorException(trace)
                stream.remove(trace)
                trace = upsample(trace, upfactor, starttime, endtime)
                if trace_sampling_rate != sampling_rate:
                    trace = decimate(trace, sampling_rate)
                stream += trace
            else:
                logging.info("Mismatched sampling rates - cannot decimate "
                             f"data from\n\t{trace}.\n..to resample data, set "
                             "resample = True and choose a suitable upfactor")

    # Trim as a general safety net. NOTE: here we are using
    # nearest_sample=False, as all data in the stream should now be at the
    # desired sampling rate, and with any off-sample data having had it's
    # timing shifted.
    stream.trim(starttime=starttime-0.00001, endtime=endtime+0.00001,
                nearest_sample=False)

    return stream


def decimate(trace, sampling_rate):
    """
    Decimate a trace to achieve the desired sampling rate, sr.

    NOTE: data will be detrended and a cosine taper applied before
    decimation, in order to avoid edge effects when applying the lowpass
    filter before decimating.

    Parameters:
    -----------
    trace : `obspy.Trace` object
        Trace to be decimated.
    sampling_rate : int
        Output sampling rate.

    Returns:
    --------
    trace : `obspy.Trace` object
        Decimated trace.

    """

    # Work on a copy of the trace
    trace = trace.copy()

    # Detrend and apply cosine taper
    trace.detrend('linear')
    trace.detrend('demean')
    trace.taper(type='cosine', max_percentage=0.05)

    # Zero-phase Butterworth-lowpass filter at Nyquist frequency
    trace.filter("lowpass", freq=float(sampling_rate) / 2.000001, corners=2,
                 zerophase=True)
    trace.decimate(factor=int(trace.stats.sampling_rate / sampling_rate),
                   strict_length=False, no_filter=True)

    return trace


def upsample(trace, upfactor, starttime, endtime):
    """
    Upsample a data stream by a given factor, prior to decimation. The
    upsampling is carried out by linear interpolation.

    NOTE: assumes any data with off-sample timing has been corrected with
    :func:`~anisotropio.utils.trace.shift_to_sample`. If not, the resulting
    traces may not all contain the correct number of samples (and desired start
    and end times).

    Parameters
    ----------
    trace : `obspy.Trace` object
        Trace to be upsampled.
    upfactor : int
        Factor by which to upsample the data in trace.

    Returns
    -------
    out : `obpsy.Trace` object
        Upsampled trace.

    """

    data = trace.data
    # Fenceposts
    dnew = np.zeros((len(data) - 1) * upfactor + 1)
    dnew[::upfactor] = data
    for i in range(1, upfactor):
        dnew[i::upfactor] = float(i)/upfactor*data[1:] \
                        + float(upfactor - i)/upfactor*data[:-1]

    # Check if start needs pad - if so pad with constant value (start value
    # of original trace). Use inequality here to only apply padding to data at
    # the start and end of the requested time window; not for other traces
    # floating in the middle (in the case that there are gaps).
    if 0. < trace.stats.starttime - starttime < trace.stats.delta:
        logging.debug(f"Mismatched starttimes: {trace.stats.starttime}, "
                      f"{starttime}")
        # Calculate how many additional samples are needed
        start_pad = np.round((trace.stats.starttime - starttime) \
            * trace.stats.sampling_rate * upfactor)
        logging.debug(f"Start pad = {start_pad}")
        # Add padding data (constant value)
        start_fill = np.full(np.int(start_pad), trace.data[0], dtype=int)
        dnew = np.append(start_fill, dnew)
        # Calculate new starttime of trace
        new_starttime = trace.stats.starttime - start_pad \
            / (trace.stats.sampling_rate * upfactor)
        logging.debug(f"New starttime = {new_starttime}")
    else:
        new_starttime = trace.stats.starttime

    # Ditto for end of trace
    if 0. < endtime - trace.stats.endtime < trace.stats.delta:
        logging.debug(f"Mismatched endtimes: {trace.stats.endtime}, {endtime}")
        # Calculate how many additional samples are needed
        end_pad = np.round((endtime - trace.stats.endtime) \
            * trace.stats.sampling_rate * upfactor)
        logging.debug(f"End pad = {end_pad}")
        # Add padding data (constant value)
        end_fill = np.full(np.int(end_pad), trace.data[-1], dtype=int)
        dnew = np.append(dnew, end_fill)

    out = Trace()
    out.data = dnew
    out.stats = trace.stats.copy()
    out.stats.npts = len(out.data)
    out.stats.starttime = new_starttime
    out.stats.sampling_rate = int(upfactor * trace.stats.sampling_rate)
    logging.debug(f"Raw upsampled trace:\n\t{out}")

    # Trim to remove additional padding left from reading with
    # nearest_sample=True at a variety of sampling rates.
    # NOTE: here we are using nearest_sample=False, as all data in the stream
    # should now be at a *multiple* of the desired sampling rate, and with any
    # off-sample data having had it's timing shifted.
    out.trim(starttime=starttime-0.00001, endtime=endtime+0.00001,
             nearest_sample=False)
    logging.debug(f"Trimmed upsampled trace:\n\t{out}")

    return out

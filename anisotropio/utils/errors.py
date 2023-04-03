# -*- coding: utf-8 -*-
"""
Module that supplies custom exceptions for the AnisotropIO package.

:copyright:
    2023, AnisotropIO developers.
:license:
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.html)

"""


class UnsetArchiveFormat(Exception):
    """Custom exception to handle case where Archive.format is not set."""

    def __init__(self):
        msg = ("Archive format has not been set. Set "
               "when making the Archive object with the kwarg "
               "'archive_format=<path_structure>', or afterwards by using the "
               "command 'Archive.path_structure(<path_structure>)'. To set a "
               "custom format, use 'Archive.format = "
               "custom/archive_{year}_{jday}/{day:02d}.{station}_structure' ")
        super().__init__(msg)


class InvalidPathToArchive(Exception):
    """
    Custom exception to handle case where an invalid path to an archive is
    provided.

    """

    def __init__(self):
        super().__init__("The archive directory specified does not exist.")


class InvalidArchivePathStructure(Exception):
    """
    Custom exception to handle case where an invalid Archive path structure
    is selected.

    """

    def __init__(self, archive_format):
        msg = ("The archive path structure you have"
               f" selected: '{archive_format}' is not a valid option! See the "
               "documentation for anisotropio.data.Archive.path_structure for"
               " a complete list, or specify a custom format with Archive.form"
               "at = custom/archive_{year}_{jday}/{day:02d}.{station}_structur"
               "e")
        super().__init__(msg)


class ArchiveEmpty(Exception):
    """Custom exception to handle empty archive"""

    def __init__(self):
        msg = "No data was available for this timestep."
        super().__init__(msg)

        # Additional message printed to log
        self.msg = ("\t\tNo files found in archive for this time period.")


class AllTracesHaveGaps(Exception):
    """
    Custom exception to handle case when all data has gaps for a given
    timestep.

    """

    def __init__(self):
        msg = ("All available data had gaps for this "
               "timestep.\n    OR: no data present in the archive for the"
               "selected stations.")
        super().__init__(msg)

        # Additional message printed to log
        self.msg = ("\t\tAll available data for this time period contains gaps"
                    "\n\t\tor data not available at start/end of time period")


# class ChannelNameException(Exception):
#     """
#     Custom exception to handle case when waveform data header has channel names
#     which do not conform to the IRIS SEED standard.

#     """

#     def __init__(self, trace):
#         msg = ("ChannelNameException: Channel name header does not conform "
#                "to\nthe IRIS SEED standard - 3 characters; ending in 'Z' for\n"
#                "vertical and ending either 'E' & 'N' or '1' & '2' for\n"
#                f"horizontal components.\n    Working on trace: {trace}")
#         super().__init__(msg)


class BadUpfactorException(Exception):
    """
    Custom exception to handle case when the chosen upfactor does not create a
    trace with a sampling rate that can be decimated to the target sampling
    rate

    """

    def __init__(self, trace):
        msg = ("chosen upfactor cannot be decimated to\n"
               f"target sampling rate.\n    Working on trace: {trace}")
        super().__init__(msg)


class ResponseNotFound(Exception):
    """
    Custom exception to handle the case where the provided response inventory
    doesn't contain the response information for a trace.

    Parameters
    ----------
    e : str
        Error message from ObsPy `Inventory.get_response()`
    tr_id : str
        ID string for the Trace for which the response cannot be found

    """

    def __init__(self, e, tr_id):
        msg = (f"{e} -- skipping {tr_id}")
        super().__init__(msg)


class ResponseRemovalFailed(Exception):
    """
    Custom exception to handle the case where the response removal was not
    successful.

    Parameters
    ----------
    e : str
        Error message from ObsPy `Trace.remove_response()` or
        `Trace.simulate()`
    tr_id : str
        ID string for the Trace for which the response cannot be removed

    """

    def __init__(self, e, tr_id):
        msg = (f"{e} -- skipping {tr_id}")
        super().__init__(msg)


# class NyquistException(Exception):
#     """
#     Custom exception to handle the case where the specified filter has a
#     lowpass corner above the signal Nyquist frequency.

#     Parameters
#     ----------
#     freqmax : float
#         Specified lowpass frequency for filter
#     f_nyquist : float
#         Nyquist frequency for the relevant waveform data
#     tr_id : str
#         ID string for the Trace

#     """

#     def __init__(self, freqmax, f_nyquist, tr_id):
#         msg = (f"    NyquistException: Selected bandpass_highcut {freqmax} "
#                f"Hz is at or above the Nyquist frequency ({f_nyquist} Hz) "
#                f"for trace {tr_id}. ")
#         super().__init__(msg)


# class TimeSpanException(Exception):
#     """
#     Custom exception to handle case when the user has submitted a start time
#     that is after the end time.

#     """

#     def __init__(self):
#         msg = ("TimeSpanException: The start time specified is after the end"
#                " time.")
#         super().__init__(msg)

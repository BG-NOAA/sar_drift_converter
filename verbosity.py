# -*- coding: utf-8 -*-
"""
******************************************************************************

 Project:     SAR Drift Converter
 Purpose:     Control how much the pipeline prints to the console. The log
              file always records everything; this governs the console only,
              so a production run can stay quiet without losing any record
              of what happened.
 Author:      Brendon Gory, brendon.gory@noaa.gov
                            brendon.gory@colostate.edu
              Data Science Application Specialist (Research Associate II)
              at CSU CIRA
 Supervisors: Dr. Ludovic Brucker, ludovic.brucker@noaa.gov
              NESDIS Physical Scientist
              Dr. Prasanjit Dash, prasanjit.dash@noaa.gov
                                  prasanjit.dash@colostate.edu
              CSU CIRA Research Scientist III
              (Program Innovation Scientist)
******************************************************************************
Copyright notice
         NOAA STAR SOCD and Colorado State Univ CIRA
         2026, Version 1.0.0
         POC: Brendon Gory (brendon.gory@noaa.gov)

 Permission is hereby granted, free of charge, to any person obtaining a
 copy of this software and associated documentation files (the "Software"),
 to deal in the Software without restriction, including without limitation
 the rights to use, copy, modify, merge, publish, distribute, sublicense,
 and/or sell copies of the Software, and to permit persons to whom the
 Software is furnished to do so, subject to the following conditions:

 The above copyright notice and this permission notice shall be included
 in all copies or substantial portions of the Software.

 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
 OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
 THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
 DEALINGS IN THE SOFTWARE.
"""


# Set once by Initialize. Module level rather than passed around: every
# module already prints, and threading a verbosity argument through every
# signature would be noise.
_level = 1

MIN_LEVEL = 0
MAX_LEVEL = 2

# Depth 1 is a pipeline stage, 2 a step within it, 3 detail within that.
# The prefix is derived rather than written at each call site, so the
# hierarchy cannot drift as messages are added.
PREFIXES = {
    1: '-->',
    2: '---->',
    3: '------>',
}


def set_level(level):
    """
    Set the console verbosity for this run.

    Parameters
    ----------
    level : int
        0 shows pipeline stages only, 1 adds the steps within them and
        the progress bars, 2 adds detail.
    """

    global _level

    _level = max(MIN_LEVEL, min(MAX_LEVEL, int(level)))


def get_level():
    """
    Current console verbosity.
    """

    return _level


def shows(depth):
    """
    Whether a message at this depth is printed.

    Notes
    -----
    Depth 1 always prints, including at level 0: a production run should
    still show which stage it is in, otherwise a stall is invisible.
    """

    return depth <= _level + 1


def echo(depth, message):
    """
    Print a message at a nesting depth, if the level allows it.

    Parameters
    ----------
    depth : int
        1 for a stage, 2 for a step, 3 for detail.

    message : str

    Notes
    -----
    Prints only. Anything worth keeping should also be logged, because
    the log file is written in full at every verbosity.
    """

    if not shows(depth):
        return

    print(f'{PREFIXES.get(depth, "")}{message}')


def progress_enabled():
    """
    Whether tqdm progress bars should be shown.

    Notes
    -----
    Off at level 0. A progress bar writes carriage returns rather than
    lines, which turns a redirected production log into one unreadable
    line, and it reports that a loop is running without saying which.
    """

    return _level >= 1

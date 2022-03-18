#!/usr/bin/env python

# MIT License
#
# Copyright (c) 2022 Qumulo
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# -----------------------------------------------------------------------------
# Logger.py
#
# Class that assists with logging errors to stdout, stderr, and/or a file.

# Import python libraries

import sys
import os
import logging
import time
from enum import Enum

#
# Build an enumeration for the logging level


class Level(Enum):
    CRITICAL = logging.CRITICAL
    ERROR = logging.ERROR
    WARNING = logging.WARNING
    INFO = logging.INFO
    DEBUG = logging.DEBUG
    NOTSET = logging.NOTSET


#
# Logger Class
#
# This class deals with using the "logging" function of python. Although it could
# be called directly within any class referencing this library, it was thought that
# encapsulating it here would make it easier to deal with. Especially for those who
# have never used logging before.


class Logger(object):
    def __init__(self, benchName="Logger", logLevel=Level.DEBUG):

        # Turn on logger and set level based upon "logLevel" argument

        self.logger = logging.getLogger(benchName)
        self.logger.setLevel(Level.DEBUG.value)
        self.logger.propagate = 1

        # Create several handlers for the logging service.
        # Set the stream handler to stderr

        logh = logging.StreamHandler()
        logh.setLevel(getattr(logging, logLevel.name))
        self.logger.addHandler(logh)

    # Change loglevel

    def setLevel(self, logLevel):

        # Find actual level value based upon name passed as argument

        if isinstance(logLevel, str):
            level = Level[logLevel]
        else:
            level = logLevel

        self.logger.setLevel(level.value)

    # Create log files

    def logFiles(self, baseDir="/tmp", model=None, version=None):

        resultsDir = self._buildResultsDir(baseDir, model, version)

        infoh = logging.FileHandler(resultsDir + "/info.log")
        infoh.setLevel(Level.INFO.value)
        self.logger.addHandler(infoh)

        errorh = logging.FileHandler(resultsDir + "/error.log")
        errorh.setLevel(Level.ERROR.value)
        self.logger.addHandler(errorh)

        debugh = logging.FileHandler(resultsDir + "/debug.log")
        debugh.setLevel(Level.DEBUG.value)
        self.logger.addHandler(debugh)

        return resultsDir

    # Write to logging using the "info" level

    def info(self, msg, *vargs):

        self.logger.info(msg, *vargs)

    # Write to logging using the "error" level

    def error(self, msg, *vargs):

        self.logger.error(msg, *vargs)

    # Write to logging using the "warning" level

    def warning(self, msg, *vargs):

        self.logger.warning(msg, *vargs)

    # Write to logging using the "debug" level

    def debug(self, msg, *vargs):

        self.logger.debug(msg, *vargs)

    # Build a results directory to store the program results. This will be
    # based upon several items: model and version of cluster, current date
    # and time.

    def _buildResultsDir(self, baseDir, model, version):

        # If they didn't pass in model and version, then we will use some defaults

        clusterModel = model if model is not None else "NoModel"
        clusterVersion = version if version is not None else "Version Info 1.0"

        # Get version... It is the third item in the array (2 starting from 0)

        info = clusterVersion.rsplit(" ")
        versinfo = info[2]

        # Get the date and time for format it

        dateinfo = time.strftime("%Y%m%d%H%M%S")

        # Build the results directory such:
        #
        # resultsdir / model / version / datetime

        resultsinfo = f"{baseDir}/{clusterModel}/{versinfo}/{dateinfo}"

        # We have to make sure that the directory is created before
        # we can use it. The assumption is that the directory does
        # not exist.

        try:
            os.makedirs(resultsinfo, 0o755)
        except Exception as excpt:
            self.logger.error(f"Error on makedirs = {excpt}")
            sys.exit(1)

        return resultsinfo


# Test Main Routine - This is not normally used as this class is usually imported


def main():

    logger = Logger("Testing")
    logger.logFiles()

    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.debug("This is a debug message")


# Main Routine

if __name__ == "__main__":
    main()
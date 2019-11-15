# coding: utf-8
#
# Python logging
# Copyright © 2018 Dave Hocker as Qalydon (qalydon17@gmail.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# See the LICENSE.md file for more details.
#

import logging
import logging.handlers
import os


class AppLogger:
    # All of the created loggers
    logger_list = []

    def __init__(self, logname):
        self.logger = None
        self.EnableLogging(logname)

    ########################################################################
    # Enable logging for the extension
    def EnableLogging(self, logname):
        if not logname in AppLogger.logger_list:
            # Default overrides
            logformat = '%(asctime)s, %(module)s, %(levelname)s, %(message)s'
            logdateformat = '%Y-%m-%d %H:%M:%S'

            self.logger = logging.getLogger(logname)

            # Default logging to DEBUG until the level is set from the configuration
            self.logger.setLevel(logging.DEBUG)

            formatter = logging.Formatter(logformat, datefmt=logdateformat)

            # Log to a file
            # Make logfile location OS specific
            # TODO This doesn't work as expect in the Ubuntu version. Need to isolate home_path function.
            if os.name == "posix":
                # Linux or OS X
                file_path = "{0}/libreoffice/qf/".format(os.environ["HOME"])
            elif os.name == "nt":
                # Windows
                file_path = "{0}\\libreoffice\\qf\\".format(os.environ["LOCALAPPDATA"])
            else:
                file_path = ""
            logfile = file_path + logname + ".log"

            # Create directory if it doesn't exist
            if not os.path.exists(file_path):
                os.makedirs(file_path, exist_ok=True)

            fh = logging.handlers.TimedRotatingFileHandler(logfile, when='midnight', backupCount=3)
            fh.setFormatter(formatter)
            self.logger.addHandler(fh)
            self.logger.debug("New logger %s created: %s", logname, str(self.logger))
            self.logger.debug("%s logging to file: %s", logname, logfile)

            # Note that this logname has been defined
            AppLogger.logger_list.append(logname)
        else:
            # Use the logger that has been previously defined
            self.logger = logging.getLogger(logname)

    def getAppLogger(self):
        """
        Return an instance of the default logger for this app.
        :return: logger instance
        """
        return self.logger

    def set_log_level(self, loglevel):
        # Logging level override (defaults to INFO)
        loglevel_setting = logging.INFO
        if loglevel:
            loglevel = loglevel.upper()
            if loglevel == "DEBUG":
                loglevel_setting = logging.DEBUG
            elif loglevel == "INFO":
                loglevel_setting = logging.INFO
            elif loglevel == "WARNING":
                loglevel_setting = logging.WARNING
            elif loglevel == "ERROR":
                loglevel_setting = logging.ERROR

        self.logger.setLevel(loglevel_setting)
        self.logger.debug("Log level set to %s", loglevel)

    # Controlled logging shutdown
    def Shutdown(self):
        self.getAppLogger().debug("Logging shutdown")
        logging.shutdown()

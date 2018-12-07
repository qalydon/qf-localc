# coding: utf-8
#
# qf_configuration - Extension configruation manager
# Copyright (C) 2018  Dave Hocker (email: Qalydon17@gmail.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the LICENSE.md file for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program (the LICENSE.md file).  If not, see <http://www.gnu.org/licenses/>.
#

import os
import os.path
import sys
import inspect
import datetime
import json
from qf_app_logger import AppLogger
from qf_url_helpers import setup_cacerts

# Logger init
the_app_logger = AppLogger("qf-extension")
logger = the_app_logger.getAppLogger()

# Python2 does not have FileNotFoundError
try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError
    logger.debug("FileNotFoundError defined")


class QConfiguration:
    """
    Encapsulates QFinance configuration data
    """
    # base_url = "https://api.qftrading.com/1.0"
    macOS = (sys.platform == "darwin")
    file_path = ""
    full_file_path = ""
    cacerts = ""
    loglevel = "info"
    cwd = ""
    qf_conf_exists = False
    qf_cache_db = "~/libreoffice/qf/qf-cache-db.sqlite3"
    qf_data_source = "wsj"
    # Experimental Stooq configuration
    qf_stooq_conf = {
        "tickerpostfix": ".us"
    }

    @classmethod
    def load(cls):
        """
        Load credentials from configuration file. The location of the qf.conf
        file is OS dependent. The permissions of the qf.conf file should allow
        access ONLY by the user.
        :return: None
        """
        file_name = "qf.conf"
        cls.file_path = QConfiguration.home_data_path()
        cls.full_file_path = cls.file_path + file_name

        # Read qf.conf file
        try:
            cf = open(cls.full_file_path, "r")
            cfj = json.loads(cf.read())

            if "loglevel" in cfj:
                cls.loglevel = cfj["loglevel"]
                the_app_logger.set_log_level(cls.loglevel)

            if "cachedb" in cfj:
                cls.qf_cache_db = cfj["cachedb"]
            else:
                # Default cache DB definition
                file_name = "qf-cache-db.sqlite3"
                if os.name == "posix":
                    # Linux or OS X
                    file_path = "{0}/libreoffice/qf/".format(os.environ["HOME"])
                elif os.name == "nt":
                    # windows
                    file_path = "{0}\\libreoffice\\qf\\".format(os.environ["LOCALAPPDATA"])
                cls.qf_cache_db = file_path + file_name
            logger.info("Using cache db %s", cls.qf_cache_db)

            # Data source can be wsj, iex. In the future maybe stooq, triingo
            if "datasource" in cfj:
                cls.qf_data_source = cfj["datasource"].lower()
            logger.info("Using data source %s", cls.qf_data_source)

            # Stooq configuration
            if "stooqconf" in cfj:
                cls.qf_stooq_conf = cfj["stooqconf"]

            cf.close()
            cls.qf_conf_exists = True
        except FileNotFoundError as ex:
            logger.error("%s was not found", cls.full_file_path)
        except Exception as ex:
            logger.error("An exception occurred while attempting to load qf.conf")
            logger.error(str(ex))

        # Set up path to certs
        cls.cwd = os.path.realpath(os.path.abspath
                                          (os.path.split(inspect.getfile
                                                         (inspect.currentframe()))[0]))
        # The embedded version of Python found in some versions of LO Calc
        # does not handle certificates. Here we compensate by using the certificate
        # package from the certifi project: https://github.com/certifi/python-certifi
        if os.name == "posix":
            cls.cacerts = "{0}/cacert.pem".format(cls.cwd)
        elif os.name == "nt":
            # This may not be necessary in Windows
            cls.cacerts = "{0}\\cacert.pem".format(cls.cwd)
        logger.debug("Path to cacert.pem: %s", cls.cacerts)
        # Attach the certs file to the URL processor
        setup_cacerts(cls.cacerts)

        # If no qf.conf file exists, create one with all defaults
        if not cls.qf_conf_exists:
            QConfiguration.save()
            # The logger defaults to debug level logging.
            # This sets the log level to whatever default was set above.
            the_app_logger.set_log_level(cls.loglevel)

    @classmethod
    def save(cls):
        """
        Save configuraton back to qf.conf
        :return:
        """

        # Make sure folders exist
        if not os.path.exists(cls.file_path):
            os.makedirs(cls.file_path)

        conf = {}
        conf["certifi"] = cls.cacerts
        conf["loglevel"] = cls.loglevel

        logger.debug("Saving configuration to %s", cls.full_file_path)
        cf = open(cls.full_file_path, "w")
        json.dump(conf, cf, indent=4)
        cf.close()

        if os.name == "posix":
            import stat
            # The user gets R/W permissions
            os.chmod(cls.full_file_path, stat.S_IRUSR | stat.S_IWUSR)
        else:
            pass

        cls.qf_conf_exists = True

    @classmethod
    def is_configured(cls):
        """
        IEX is configured if the qf.conf file exists
        :return:
        """

        return cls.qf_conf_exists

    @staticmethod
    def home_data_path():
        if os.name == "posix":
            # Linux or OS X
            return "{0}/libreoffice/qf/".format(os.environ["HOME"])
        elif os.name == "nt":
            # Windows
            return "{0}\\libreoffice\\qf\\".format(os.environ["LOCALAPPDATA"])
        return ""

# Set up configuration
QConfiguration.load()

# coding: utf-8
#
# QFinance home directory finder
# Copyright © 2020  Dave Hocker (email: qalydon17@gmail.com)
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
import platform


def find_emergency_home(logger=None):
    """
    Find the directory to be used for emergency error reporting
    :param logger: Optional logger instance
    :return:
    """
    if "QF_LOCALC_LOG_DIR" in os.environ.keys():
        home_path = os.environ["QF_LOCALC_LOG_DIR"]
    elif os.name == "posix":
        key = None
        if "USER" in os.environ.keys():
            key = "USER"
        elif "USERNAME" in os.environ.keys():
            key = "USERNAME"
        if key is not None:
            # macOS X versus *nix
            if platform.system() == "Darwin":
                home_path = "/Users/{0}/libreoffice/qf/".format(os.environ[key])
            else:
                home_path = "/home/{0}/libreoffice/qf/".format(os.environ[key])
        else:
            # Under Snap, this will be hard to find
            home_path = "{0}/libreoffice/qf/".format(os.environ["HOME"])
    elif os.name == "nt":
        # Windows
        home_path = os.environ["HOMEPATH"] + "/libreoffice"
    else:
        home_path = ""
    if logger is not None:
        logger.info("The emergency home path is: %s", home_path)

    return home_path


def find_home(logger=None):
    """
    Find the nominal home directory
    :param logger: Optional logger instance
    :return:
    """
    if "SNAP" in os.environ.keys() and logger is not None:
        logger.info("LibreOffice is running under SNAP")

    if "QF_LOCALC_LOG_DIR" in os.environ.keys():
        home_path = os.environ["QF_LOCALC_LOG_DIR"]
    elif os.name == "posix":
        # Linux or OS X
        # We are trying to force the directory to a well known location
        key = None
        if "USER" in os.environ.keys():
            key = "USER"
        elif "USERNAME" in os.environ.keys():
            key = "USERNAME"
        if key is not None:
            # macOS X versus *nix
            if platform.system() == "Darwin":
                home_path = "/Users/{0}/libreoffice/qf/".format(os.environ[key])
            else:
                home_path = "/home/{0}/libreoffice/qf/".format(os.environ[key])
        else:
            # Under Snap, this will be hard to find
            home_path = "{0}/libreoffice/qf/".format(os.environ["HOME"])
    elif os.name == "nt":
        # Windows
        home_path = "{0}\\libreoffice\\qf\\".format(os.environ["LOCALAPPDATA"])
    else:
        home_path = ""
    if logger is not None:
        logger.info("The home path is: %s", home_path)

    return home_path
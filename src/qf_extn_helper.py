# coding: utf-8
#
# LO Calc extension helpers
# Copyright (C) 2017  Dave Hocker as Qalydon (email: qalydon17@gmail.com)
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
# References
# https://wiki.openoffice.org/wiki/Calc/Add-In/Python_How-To
# http://www.biochemfusion.com/doc/Calc_addin_howto.html
# https://github.com/madsailor/SMF-Extension
#

import datetime
import os
import inspect
import xml.etree.ElementTree as etree
# from qf_configuration import QConfiguration
from qf_app_logger import AppLogger

# Logger init
the_app_logger = AppLogger("qf-extension")
logger = the_app_logger.getAppLogger()


def qf_version():
    """
    Extract version from description.xml
    :return: Version string n.n.n
    """
    cmd_folder = os.path.realpath(os.path.abspath
                                  (os.path.split(inspect.getfile
                                                 ( inspect.currentframe() ))[0]))
    tree = etree.parse(cmd_folder + "/description.xml")
    root = tree.getroot()
    nodes = root.findall('{http://openoffice.org/extensions/description/2006}version')
    return nodes[0].attrib["value"]


def float_to_date_str(float_date):
    """
    Magic algorithm to convert float date
    LibreOffice date as a float (actually the format used by Excel)
    base_date = 1899-12-30 = the float value 0.0
    see this reference: http://www.cpearson.com/excel/datetime.htm
    :param float_date: ddddd.tttttt where d is days from 1899-12-31 and .tttttt is fraction of 24 hours
    :return:
    """
    # 25569 = number of days from 1899-12-30 to 1970-1-1
    # 86400 = number of seconds in a day
    # seconds = number of seconds from 1970-1-1 00:00:00
    seconds = (int(float_date) - 25569) * 86400
    d = datetime.datetime.utcfromtimestamp(seconds)
    eff_date = d.strftime("%Y-%m-%d")
    return eff_date

def date_str_to_float(date_str):
    """
    Magic algorithm to convert an ISO date string (e.g. 2017-07-11 12:49:12 +0000)
    to a LibreOffice date as a float.
    :param date_str: Date to be converted.
    :return:
    """
    dt = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S %z")
    # Here, timestamp() is the number of seconds from 1970-1-1 00:00:00
    # 25569.0 = number of days from 1899-12-30 to 1970-1-1
    # 86400.0 = number of seconds in a day
    float_date = (dt.timestamp() / 86400.0) + 25569.0
    # The result is a float of the form ddddd.tttttt where ddddd is the number of days
    # since 1899-12-31 and .tttttt is the fractional portion of a day.
    return float_date

def normalize_date(tgtdate):
    """
    Normalize an LO Calc date to an ISO formatted string
    :param tgtdate: The date can be a float or a string. Floats are
    in an Excel format (see float_to_date-str() above). Strings are
    in ISO format YYYYY-MM-DD or US format m/d/yy.
    :return: Returns the date normalized to an ISO format string.
    """
    if type(tgtdate) == float:
        if tgtdate == 0.0:
            return None
        return float_to_date_str(tgtdate)
    elif type(tgtdate) == str and tgtdate != "":
        # Assumed to be a string in ISO format (YYYY-MM-DD).
        try:
            dt = datetime.datetime.strptime(tgtdate, "%Y-%m-%d")
            return tgtdate
        except Exception:
            pass
        try:
            # Try date as mm/dd/yy
            dt = datetime.datetime.strptime(tgtdate, "%m/%d/%y")
            return dt.strftime("%Y-%m-%d")
        except Exception:
            pass
    elif tgtdate is None or tgtdate == "":
        return tgtdate

    raise ValueError("Unsupported date format type: {0} value: {1}".format(type(tgtdate), tgtdate))

def normalize_frequency(frequency):
    """
    Normalize frequency to account for the way LO Calc delivers empty cells
    :param frequency:
    :return:
    """
    if type(frequency) == str:
        return frequency
    elif type(frequency) == float:
        return None
    return str(frequency)
# coding: utf-8
#
# QFinance extension main interface to LO Calc
# Copyright © 2018  Dave Hocker (email: qalydon17@gmail.com)
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

try:
    import os
    import sys
    import inspect
    import threading
    import datetime
    import unohelper
    from com.qf.api.localc import XQFinance

    # Add current directory to path to import local modules
    cmd_folder = os.path.realpath(os.path.abspath
                                  (os.path.split(inspect.getfile
                                                 ( inspect.currentframe() ))[0]))
    if cmd_folder not in sys.path:
        sys.path.insert(0, cmd_folder)

    # Local imports go here
    from qf_app_logger import AppLogger
    import xml.etree.ElementTree as etree
    from qf_configuration import QConfiguration
    from qf_extn_helper import qf_version, normalize_date
    # These imports were moved to the methods that use them as a form of late binding.
    # On Windows 10 they cause an obscure error if Sqlite3 is not available.
    # import qf_hist_quote
    # import qf_dividends
    # from qf_data_source_mgr import DataSourceMgr

    # Logger init
    the_app_logger = AppLogger("qf-extension")
    logger = the_app_logger.getAppLogger()
    # Log embedded Python version
    logger.info("Using Python %s", sys.version)
    # Extract extension version from description.xml
    _qf_version = qf_version()
    logger.info("QF-LOCalc Version: %s", _qf_version)
    # After logger
    logger.debug("Dumping evnironment")
    for key in os.environ.keys():
        logger.debug("[%s]=%s", key, os.environ[key])
except Exception as ex:
    # Emergency debugging to cover for the fact that LibreOffice is terrible at debugging...
    # The first choice of location for the emergency log is the environment setting
    if "QF_LOCALC_LOG_DIR" in os.environ.keys():
        home_path = os.environ["QF_LOCALC_LOG_DIR"]
    elif os.name == "posix":
        key = None
        if "USER" in os.environ.keys():
            key = "USER"
        elif "USERNAME" in os.environ.keys():
            key = "USERNAME"
        if key is not None:
            home_path = "/home/{0}/libreoffice/qf/".format(os.environ[key])
        else:
            # Under Snap, this will be hard to find
            home_path = "{0}/libreoffice/qf/".format(os.environ["HOME"])
    elif os.name == "nt":
        home_path = os.environ["HOMEPATH"] + "/libreoffice"
    else:
        home_path = ""
    # Make sure the emergency log directory exists
    if not os.path.exists(home_path):
        os.makedirs(home_path)
    emergency_log = "{0}/error_report.txt".format(home_path)
    fh = open(emergency_log, "a")
    fh.write(str(ex))
    fh.write("\n")
    fh.close()
    exit(666)

class QFImpl(unohelper.Base, XQFinance):
    """Define the main class for the QFinance LO Calc extension """
    def __init__( self, ctx ):
        self.ctx = ctx
        logger.debug("QFImpl initialized")
        logger.debug("self: %s", str(self))
        logger.debug("ctx: %s", str(ctx))

    def QFVersion(self):
        logger.debug("QFVersion called %s", _qf_version)
        return _qf_version

    def QFDataSource(self, category):
        if category and category in QConfiguration.qf_data_sources.keys():
            logger.debug("QFDataSource called for category %s: %s", category, str(QConfiguration.qf_data_sources[category]))
            return str(QConfiguration.qf_data_sources[category])

        # The default is the data source list for stocks
        logger.debug("QFDataSource called for default category: %s", str(QConfiguration.qf_data_sources["stock"]))
        return str(QConfiguration.qf_data_sources["stock"])

    def QFClosingPrice(self, symbol, category, fordate):
        import qf_hist_quote
        valid = self.__validate_parms(symbol, category, fordate)
        if (valid[0]):
            logger.debug("QFClosingPrice called %s %s %s", symbol, category, fordate)
            return qf_hist_quote.closing_price(symbol, category, fordate)
        return valid[1]

    def QFOpeningPrice(self, symbol, category, fordate):
        import qf_hist_quote
        logger.debug("QFOpeningPrice called %s %s %s", symbol, category, fordate)
        valid = self.__validate_parms(symbol, category, fordate)
        if (valid[0]):
            return qf_hist_quote.opening_price(symbol, category, fordate)
        return valid[1]

    def QFHighPrice(self, symbol, category, fordate):
        import qf_hist_quote
        logger.debug("QFHighPrice called %s %s %s", symbol, category, fordate)
        valid = self.__validate_parms(symbol, category, fordate)
        if (valid[0]):
            return qf_hist_quote.high_price(symbol, category, fordate)
        return valid[1]

    def QFLowPrice(self, symbol, category, fordate):
        import qf_hist_quote
        logger.debug("QFLowPrice called %s %s %s", symbol, category, fordate)
        valid = self.__validate_parms(symbol, category, fordate)
        if (valid[0]):
            return qf_hist_quote.low_price(symbol, category, fordate)
        return valid[1]

    def QFDayVolume(self, symbol, category, fordate):
        import qf_hist_quote
        logger.debug("QFDayVolume called %s %s %s", symbol, category, fordate)
        valid = self.__validate_parms(symbol, category, fordate)
        if (valid[0]):
            return qf_hist_quote.daily_volume(symbol, category, fordate)
        return valid[1]

    def QFTTMDividend(self, symbol, fordate):
        import qf_dividends
        logger.debug("QFTTMDividend called %s %s", symbol, fordate)
        valid = self.__validate_parms(symbol, "", fordate)
        if (valid[0]):
            return qf_dividends.ttm_dividend(symbol, fordate)
        return valid[1]

    def __validate_parms(self, symbol, category, fordate):
        """
        Validate historical function parameters
        :param symbol: Not blank
        :param category: "", stock, etf, mutf, mutualfund or index
        :param fordate: yyyy-mm-dd or mm/dd/yy or LOCalc float date
        :return: (valid, message)
        """
        if not symbol:
            return (False, "Invalid ticker symbol")
        if category.lower() not in ["", "stock", "etf", "mutf", "mutualfund", "index"]:
            return (False, "Invalid category")
        if type(fordate) == float:
            # Date is a LOCalc float date
            normalized_dt = normalize_date(fordate)
            dt = datetime.datetime.strptime(normalized_dt, "%Y-%m-%d")
            d = datetime.date(dt.year, dt.month, dt.day)
            if datetime.date.today() <= d:
                # The date cannot be in the future
                return (False, "Date must be in the past")
        elif type(fordate) == str and fordate != "":
            # Assumed to be a string in ISO format (YYYY-MM-DD).
            try:
                dt = datetime.datetime.strptime(fordate, "%Y-%m-%d")
            except Exception:
                try:
                    # Try date as mm/dd/yy
                    dt = datetime.datetime.strptime(fordate, "%m/%d/%y")
                except Exception:
                    # Failed both date format checks
                    return (False, "Invalid date")
            d = datetime.date(dt.year, dt.month, dt.day)
            if datetime.date.today() <= d:
                # The date cannot be in the future
                return (False, "Date must be in the past")
        else:
            return (False, "Invalid date type or format")
        # All checks passed
        return (True, "")

#
# Boiler plate code for adding an instance of the extension
#

def createInstance( ctx ):
    return QFImpl( ctx )

g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationHelper.addImplementation( \
    createInstance,"com.qf.api.localc.python.QFImpl",
        ("com.sun.star.sheet.AddIn",),)

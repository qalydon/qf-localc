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
    from qf_extn_helper import qf_version
    import qf_hist_quote

    # Logger init
    the_app_logger = AppLogger("qf-extension")
    logger = the_app_logger.getAppLogger()
    # Extract version from description.xml
    _qf_version = qf_version()
    logger.info("QF-LOCalc Version: %s", _qf_version)
    # After logger
except Exception as ex:
    # Emergency debugging to cover for the fact that LibreOffice is terrible at debugging...
    # from qf_configuration import QConfiguration
    # fh = open(QConfiguration.home_data_path() + "error_report.txt", "a")
    fh = open("/Users/dhocker/libreoffice/error_report.txt", "a")
    # fh.write(ex)
    fh.write(str(ex))
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

    def QFClosingQuote(self, symbol, category, fordate):
        logger.debug("QFClosingQuote called %s %s %s", symbol, category, fordate)
        return qf_hist_quote.closing_price(symbol, category, fordate)


#
# Boiler plate code for adding an instance of the extension
#

def createInstance( ctx ):
    return QFImpl( ctx )

g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationHelper.addImplementation( \
    createInstance,"com.qf.api.localc.python.QFImpl",
        ("com.sun.star.sheet.AddIn",),)

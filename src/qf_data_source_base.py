# coding: utf-8
#
# Base class for a data source
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

from qf_app_logger import AppLogger

# Logger init
the_app_logger = AppLogger("qf-extension")
logger = the_app_logger.getAppLogger()


class DataSourceBase:
    """
    A data source class must implement each method define here
    """
    def __init__(self):
        pass

    def get_historical_price_data(self, ticker, category, for_date):
        """
        Get historical price data for a ticker symbol
        :param ticker: djia, spx, comp for common indices. Otherwise, a stock symbol.
        :param category: stock, etf, mutf or mutualfund, index. A data source
        can support one or more of these. It does not have to support all of them.
        :param for_date: format YYYYMMDD (no embedded / or -)
        :return: OHLC with date in JSON format
        """
        return {}

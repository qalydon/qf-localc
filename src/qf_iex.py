# coding: utf-8
#
# qf_iex - Implements the IEX based data acquisition
# Copyright © 2018  Dave Hocker (email: Qalydon17@gmail.com)
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
from datetime import datetime
import urllib.request
import json

# Logger init
the_app_logger = AppLogger("qf-extension")
logger = the_app_logger.getAppLogger()


def get_historical_price_data(symbol, category, for_date):
    """
    Call IEX API to get the price data for a given symbol on
    a given date. This method uses the IEX chart URL to fetch
    daily chart data for the smallest period containing the for_date.
    The maximum is 5 years.
    :param ticker:
    :param category: Not used. IEX only works for stocks and etfs
    :param for_date
    :return:
    """
    if category not in ["", "stock", "etf"]:
        raise ValueError("IEX only supports categories stock and etf")

    # Determine the width of the chart data based on the for_date
    # This can be 1m, 3m, 6m, 1y, 2y or 5y
    diff = datetime.now() - datetime.strptime(for_date, "%Y-%m-%d")
    if diff.days <= 30:
        period = "1m"
    elif diff.days <= 90:
        period = "3m"
    elif diff.days <= 180:
        period = "6m"
    elif diff.days <= 365:
        period = "1y"
    elif diff.days <= (365 * 2):
        period = "2y"
    else:
        period = "5y"

    url = "https://api.iextrading.com/1.0/stock/{0}/chart/{1}".format(symbol.upper(), period)
    logger.debug("Calling %s", url)
    try:
        with urllib.request.urlopen(url) as testfile:
            json_data = testfile.read().decode()
            res = json.loads(json_data)
            # IEX returns a list of dicts where each dict is a day.
            # Useful data in each dict is date, OHLC and volume
            # There are other more sophisticated ways to search a list.
            # This one has the advantage of stopping as soon as a match is found.
            for day in res:
                if day["date"] == for_date:
                    return day
    except Exception as ex:
        pass

    logger.error("Chart data for {0} on date {1} was not found".format(symbol.upper(), for_date))
    return {}

# coding: utf-8
#
# qf_iex - Implements the IEX Version 1.0 API based data acquisition
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
from qf_data_source_base import DataSourceBase
from qf_extn_helper import normalize_date
from datetime import datetime, timedelta
import urllib.request
import json

# Logger init
the_app_logger = AppLogger("qf-extension")
logger = the_app_logger.getAppLogger()


class IEXDataSource(DataSourceBase):
    # Period to days conversion
    _period_lookup_table = {
        "1m": 30,
        "3m": 90,
        "6m": 180,
        "1y": 365,
        "2y": 365 * 2,
        "5y": 365 * 5
    }
    def __init__(self):
        super(IEXDataSource, self).__init__()

    def get_historical_price_data(self, symbol, category, for_date):
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

    def get_dividend_data(self, symbol, for_date, period):
        """
        Get dividend distributions for the given symbol and period. During the development of
        this method it was discovered that the IEX dividend data available through the
        IEX 1.0 API has not been updated since March 2018. Apparently, up-to-date dividend
        data can only be obtained through the new IEX Cloud API. The new API has limited free
        use with an emphasis of moving users to a pay wall (https://iexcloud.io/pricing/).
        :param symbol: ticker symbol
        :param for_date: period ending date
        :param period: 1m, 3m, 6m, 1y, 2y, 5y. TTM = 1y.
        :return: list of dividend distributions in period. See https://iextrading.com/developer/docs/#dividends
        for a definition of the returned list.
        [
            {
                "exDate": "2018-02-08",
                "paymentDate": "2018-03-10",
                "recordDate": "2018-02-09",
                "declaredDate": "2018-01-30",
                "amount": 1.5,
                "flag": "FI",
                "type": "Dividend income",
                "qualified": "",
                "indicated": ""
            },
            ...
        ]
        """
        # Fetch max amount of data. We'll filter it as necessary.
        url = "https://api.iextrading.com/1.0/stock/{0}/dividends/{1}".format(symbol.upper(), "5y")
        logger.debug("Calling %s", url)

        filtered_list = []
        try:
            with urllib.request.urlopen(url) as testfile:
                json_data = testfile.read().decode()
                # IEX returns a list of dicts where each dict is a dividend distribution.
                res = json.loads(json_data)

                end_date = datetime.strptime(normalize_date(for_date), "%Y-%m-%d")
                start_date = end_date - timedelta(days=IEXDataSource._period_lookup_table[period])

                # Filter the results list to those distributions within the period
                for dist in res:
                    dist_date = datetime.strptime(dist["declaredDate"], "%Y-%m-%d")
                    if (start_date < dist_date) and (dist_date < end_date):
                        filtered_list.append(dist)
        except Exception as ex:
            filtered_list = []
            logger.error(ex)
            logger.error("Dividend data for {0} period {1} was not returned".format(symbol.upper(), period))

        return filtered_list

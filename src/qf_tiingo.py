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
from qf_data_source_base import DataSourceBase
from qf_configuration import QConfiguration
from qf_tiingo_support import api_key
from datetime import datetime
import urllib.request
import json

# Logger init
the_app_logger = AppLogger("qf-extension")
logger = the_app_logger.getAppLogger()


class TiingoDataSource(DataSourceBase):
    def __init__(self):
        super(TiingoDataSource, self).__init__()

    def get_historical_price_data(self, symbol, category, for_date):
        """
        Call Tiingo API to get the price data for a given symbol on
        a given date.
        :param symbol: ticker symbol
        :param category: Not used. Tiingo only works for stocks, etfs and mutfs.
        Index is not supported.
        :param for_date
        :return:
        """
        if category not in ["", "stock", "etf", "mutf"]:
            raise ValueError("Tiingo only supports categories stock, etf and mutf")

        try:
            apitoken = QConfiguration.qf_tiingo_conf["apitoken"]
        except Exception as ex:
            apitoken = None
        if not apitoken:
            # Ask for the API key
            # Returns a tuple
            res = api_key()
            if res[0]:
                # Save the API key in the configuration file
                QConfiguration.qf_tiingo_conf["apitoken"] = res[1]
                logger.info("Tiingo API key has been set")
                QConfiguration.save()
                apitoken = res[1]
            else:
                raise ValueError("Tiingo requires an API token")

        url = "https://api.tiingo.com/tiingo/daily/{0}/prices?startDate={1}&endDate={2}&token={3}"
        url = url.format(symbol.upper(), for_date, for_date, apitoken)

        # Log URL without API token
        masked_url = "https://api.tiingo.com/tiingo/daily/{0}/prices?startDate={1}&endDate={2}&token={3}"
        masked_url = masked_url.format(symbol.upper(), for_date, for_date, "*" * len(apitoken))
        logger.debug("Calling %s", masked_url)

        try:
            with urllib.request.urlopen(url) as testfile:
                json_data = testfile.read().decode()
                res = json.loads(json_data)
                # Tiingo returns a JSON response that is a list.
                return res[0]
        except Exception as ex:
            logger.error(str(ex))

        logger.error("Data for {0} on date {1} was not found".format(symbol.upper(), for_date))
        return {}


if __name__ == '__main__':
    # Basic test of Tiingo
    for_date = '2018-11-30'
    ticker = 'aapl'
    ds = TiingoDataSource()
    try:
        d = ds.get_historical_price_data(ticker, "etf", for_date)
        if d:
            print(ticker)
            print(json.dumps(d, indent=4))
    except Exception as ex:
        print(ex)

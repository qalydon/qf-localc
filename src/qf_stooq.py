# coding: utf-8
#
# Download historical data from stooq.com
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

import urllib.request
import datetime
from qf_app_logger import AppLogger
from qf_data_source_base import DataSourceBase
from qf_configuration import QConfiguration

# Logger init
the_app_logger = AppLogger("qf-extension")
logger = the_app_logger.getAppLogger()

# Index mapping for Stooq
index_map = {
    "djia": "^dji",
    "spx": "^spx",
    "nasdaq": "^ndq"
}

class StooqDataSource(DataSourceBase):
    def __init__(self):
        super(StooqDataSource, self).__init__()

    def get_historical_price_data(self, ticker, category, for_date):
        """
        Get historical price data for a stock ticker symbol. Note that Stooq only
        seems to support stocks and certain indexes. It does not support ETFs or MUTFs.
        :param ticker: ^dji, ^spx, ^ndq for common indices. Otherwise, a stock symbol.
        :param category: Not used by Stooq
        :param for_date: format YYYYMMDD (no embedded / or -). The format is automatically cleaned.
        :return: OHLC with date in JSON format
        """
        # Remap symbol if necessary
        ticker = ticker.lower()
        if ticker in index_map.keys():
            ticker = index_map[ticker]
        else:
            # By observation all US tickers end with .us
            # Here we use the configured postfix
            # if the ticker does not already have the postfix
            if not ticker.endswith(QConfiguration.qf_stooq_conf["tickerpostfix"]):
                ticker += QConfiguration.qf_stooq_conf["tickerpostfix"]
            # ticker += ".us"

        # As of 2018-12-06 this URL consistently returns "No data" as if the request is black-listed
        url = 'https://stooq.com/q/d/l/?s={0}&d1={1}&d2={1}&i=d'.format(ticker, for_date.replace('-', ''))
        logger.debug("Calling %s", url)
        try:
            with urllib.request.urlopen(url) as testfile:
                csv_data = testfile.read().decode()
                # This code depends on the first line of the result being the column names
                # and the second line being the data for the date. All lines after the second
                # line are ignored.
                # Data looks like this:
                # 'Date', 'Open', 'High', 'Low', 'Close', 'Volume'
                #  '2018-12-06', '199.61', '203.08', '198.19', '202.68', '2991766'
                lines = csv_data.splitlines()
                # The response must contain at least 2 lines
                if len(lines) < 2:
                    logger.error(url)
                    logger.error("Did not return a response")
                    return None

                a = []
                for line in lines:
                    if line:
                        a.append(line.split(','))
                d = {}
                # Only for the number of columns in the response.
                # Some responses have more than Date/OHLC columns.
                for i in range(len(a[0])):
                    key = a[0][i].lower().strip()
                    try:
                        d[key] = float(a[1][i])
                    except:
                        if key == "date":
                            # Date - Stooq uses ISO format YYYY-mm-dd
                            d[key] = a[1][i]
                        else:
                            # Not date
                            d[key] = a[1][i]
        except Exception as ex:
            d = None
            raise ex

        return d

if __name__ == '__main__':
    # ticker = '^dji'
    for_date = '2018-11-30'
    # d = get_stooq_price_data(ticker, for_date)
    # print("Closing price for:", ticker, for_date, d["close"])
    #
    # ticker = '^spx'
    # d = get_stooq_price_data(ticker, for_date)
    # print("Closing price for:", ticker, for_date, d["close"])
    #
    # ticker = '^ndq'
    # d = get_stooq_price_data(ticker, for_date)
    # print("Closing price for:", ticker, for_date, d["close"])

    ticker = 'mint'
    ds = StooqDataSource()
    try:
        d = ds.get_historical_price_data(ticker, "", for_date)
        if d:
            print("Closing price for:", ticker, for_date, d["close"])
    except Exception as ex:
        print(ex)

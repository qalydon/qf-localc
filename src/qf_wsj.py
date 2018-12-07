# coding: utf-8
#
# Download historical data from wsj.com
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
# Download historical data from wsj.com
# Note how URL uses etf, mutualfund, index
# https://quotes.wsj.com/etf/MINT/historical-prices/download?MOD_VIEW=page&num_rows=90.04166666666667&range_days=90.04166666666667&startDate=09/04/2018&endDate=12/03/2018
# https://quotes.wsj.com/mutualfund/{0}/historical-prices/download?MOD_VIEW=page&num_rows=3&range_days=3&startDate=11/30/2018&endDate=12/01/2018
# https://quotes.wsj.com/index/DJIA/historical-prices/download?MOD_VIEW=page&num_rows=90.04166666666667&range_days=90.04166666666667&startDate=09/04/2018&endDate=12/03/2018
# Note how a regular stock has no category qualifier
# https://quotes.wsj.com/AAPL/historical-prices/download?MOD_VIEW=page&num_rows=90.04166666666667&range_days=90.04166666666667&startDate=09/04/2018&endDate=12/03/2018
#

import urllib.request
import datetime
from qf_data_source_base import DataSourceBase
from qf_app_logger import AppLogger

# Logger init
the_app_logger = AppLogger("qf-extension")
logger = the_app_logger.getAppLogger()

# Index mapping for Stooq
index_map = {
    "djia": "djia",
    "spx": "spx",
    "nasdaq": "comp"
}

# For WSJ
wsj_category_map = {
    "stock": "",
    "mutf": "mutualfund",
    "mutualfund": "mutualfund",
    "etf": "etf",
    "index": "index"
}

class WSJDataSource(DataSourceBase):
    def __init__(self):
        super(WSJDataSource, self).__init__()

    def get_historical_price_data(self, ticker, category, for_date):
        """
        Get historical price data for a ticker symbol
        :param ticker: djia, spx, comp for common indices. Otherwise, a stock symbol.
        :param category: stock, etf, mutf or mutualfund, index. A data source
        can support one or more of these. It does not have to support all of them.
        :param for_date: format YYYYMMDD (no embedded / or -)
        :return: OHLC with date in JSON format
        """
        # Remap symbol if necessary
        ticker = ticker.lower()
        if ticker in index_map.keys():
            ticker = index_map[ticker]

        # Validate/translate category
        if category:
            if category.lower() in wsj_category_map.keys():
                category = wsj_category_map[category.lower()]
            else:
                raise ValueError("Invalid category")
        else:
            category = ""

        # url = 'https://quotes.wsj.com/mutualfund/{0}/historical-prices/download?MOD_VIEW=page&num_rows=3&range_days=3&startDate=11/30/2018&endDate=12/01/2018'.format(ticker)
        # ISO date format seems to be accepted. However, the date in the data is mm/dd/yy.
        # Must compute next date after for-date
        end_date_dt = datetime.datetime.strptime(for_date, "%Y-%m-%d") + datetime.timedelta(days=1)
        end_date = end_date_dt.strftime("%Y-%m-%d")
        if category:
            url = 'https://quotes.wsj.com/{0}/{1}/historical-prices/download?MOD_VIEW=page&num_rows=3&range_days=3&startDate={2}&endDate={3}'.format(
                category, ticker, for_date, end_date)
        else:
            url = 'https://quotes.wsj.com/{0}/historical-prices/download?MOD_VIEW=page&num_rows=3&range_days=3&startDate={1}&endDate={2}'.format(
                ticker, for_date, end_date)
        logger.debug("Calling %s", url)

        try:
            with urllib.request.urlopen(url) as testfile:
                csv_data = testfile.read().decode()
                # This code depends on the first line of the result being the column names
                # and the second line being the data for the date. No attempt is made to
                # go beyond the second line of the response.
                # Example
                # Date, Open, High, Low, Close
                # 11/30/18, 10.14, 10.14, 10.14, 10.14
                lines = csv_data.splitlines()
                a = []
                for line in lines:
                    if line:
                        a.append(line.split(','))
                d = {}
                for i in range(5):
                    key = a[0][i].lower().strip()
                    try:
                        d[key] = float(a[1][i])
                    except:
                        if key == "date":
                            # Date - reformat from mm/dd/yy to ISO format YYYY-mm-dd
                            for_date_dt = datetime.datetime.strptime(a[1][i], "%m/%d/%y")
                            d[key] = for_date_dt.strftime("%Y-%m-%d")
                        else:
                            # Not date
                            d[key] = a[1][i]
                # WSJ does not provide volume, so we stub it out
                d["volume"] = 0

                # print(d)
        except Exception as ex:
            print(ex)

        return d


if __name__ == '__main__':
    wsj = WSJDatasource()

    d = wsj.get_historical_price_data("ussbx", "mutualfund", "2018-11-30")
    print("ussbx", d)

    d = wsj.get_historical_price_data("mint", "etf", "2018-11-30")
    print("mint", d)

    d = wsj.get_historical_price_data("aapl", "", "2018-11-30")
    print("aapl", d)

    # Major indexes

    d = wsj.get_historical_price_data("djia", "index", "2018-11-30")
    print("DJIA", d)

    d = wsj.get_historical_price_data("spx", "index", "2018-11-30")
    print("S&P 500", d)

    d = wsj.get_historical_price_data("comp", "index", "2018-11-30")
    print("NASDAQ", d)
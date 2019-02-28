# coding: utf-8
#
# Download historical data from Yahoo
# Copyright © 2019  Dave Hocker (email: qalydon17@gmail.com)
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
# Attribution
# -----------
#
# This code was adapted from the pandas-datareader project.
# See https://github.com/pydata/pandas-datareader. The original source can be found at:
# https://github.com/pydata/pandas-datareader/blob/master/pandas_datareader/yahoo/daily.py
#
# While no disclaimer or copyright was found in the original source, it is believed that the
# source is subject to the following license:
# https://github.com/pydata/pandas-datareader/blob/master/LICENSE.md
#
# In any case, GPLv3 as noted above applies where no other license applies.
#

import json
import re
import time
import datetime
import urllib.request
from qf_app_logger import AppLogger
from qf_data_source_base import DataSourceBase
from qf_configuration import QConfiguration

# Logger init
the_app_logger = AppLogger("qf-extension")
logger = the_app_logger.getAppLogger()


class YahooDataSource(DataSourceBase):

    # Index mapping for Yahoo
    _index_map = {
        "djia": "^DJI",
        "spx": "^GSPC",
        "nasdaq": "^IXIC"
    }

    # Pacing control, hopefully to avoid getting throttled or banned
    # This value is shared across all instances of the data source
    # and NO attempt is made to syncrhonize access to it. The
    # worst outcome is that extra pacing will occur.
    _last_request_time = datetime.datetime.now()
    _pause = float(QConfiguration.qf_yahoo_conf["pacing"]) # float, seconds (e.g. 0.200)

    # Not sure we need the Connection header.
    # The User-Agent header probably makes requests look like they came from a browser
    _headers = {
        'Connection': 'keep-alive',
        'Expires': str(-1),
        'Upgrade-Insecure-Requests': str(1),
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'
    }

    def __init__(self):
        super(YahooDataSource, self).__init__()

    @property
    def _url(self):
        """
        Template URL for Yahoo historical data web page
        :return:
        """
        # The template contains substituion points for ticker, starting date and ending date
        return 'https://finance.yahoo.com/quote/{}/history?period1={}&period2={}&interval=1d&filter=history&frequency=1d'

    def get_historical_price_data(self, symbol, category, for_date):
        """
        Essentially a page scrape of a Yahoo page containing historical data
        :param symbol: ticker symbol
        :param category: not used
        :param for_date: yyyy-mm-dd ISO format
        :return: dict of OHLCV results
        """

        # Normalize ticker symbol if it's an index
        ticker = symbol.lower()
        if ticker in YahooDataSource._index_map.keys():
            symbol = YahooDataSource._index_map[ticker]

        # Convert for_date to Unix time.  The 4 hour adjustment is a mystery (from original code).
        four_hours_in_seconds = 14400
        dt = datetime.datetime.strptime(for_date, "%Y-%m-%d")
        unix_for_date = int(time.mktime(dt.timetuple()))
        unix_for_date += four_hours_in_seconds

        url = self._url.format(symbol, unix_for_date, unix_for_date)
        # url => https://finance.yahoo.com/quote/AAPL/history?period1=1519753902&period2=1551289902&interval=1d&filter=history&frequency=1d
        req = urllib.request.Request(url, headers=YahooDataSource._headers)
        logger.debug("Calling %s", url)

        # Apply pacing, avoid getting throttled
        elapsed = datetime.datetime.now() - YahooDataSource._last_request_time
        if elapsed.total_seconds() < YahooDataSource._pause:
            time.sleep(YahooDataSource._pause)
            logger.debug("Pacing %f...", YahooDataSource._pause)
        YahooDataSource._last_request_time = datetime.datetime.now()

        # Send the request and read the response
        try:
            with urllib.request.urlopen(req) as page_source:
                resp = page_source.read().decode()
        except Exception as ex:
            logger.error(ex)
            raise ex

        # This page scraping technique is highly subject to breakage. It is likely
        # that changes will be required at the least expected time :-)
        # Here is some regex magic. It finds the data rows in the middle of the web page.
        ptrn = r'root\.App\.main = (.*?);\n}\(this\)\);'
        try:
            j = json.loads(re.search(ptrn, resp, re.DOTALL).group(1))
            data = j['context']['dispatcher']['stores']['HistoricalPriceStore']
            # return the first row of data (we only asked for one date)
            prices = data['prices'][0]
        except Exception as ex:
            logger.error(ex)
            msg = 'No data fetched for symbol {} using {}'
            raise ValueError(msg.format(symbol, "Yahoo"))

        # Notes
        # All keys appear to be in lower case
        # Date is in unix time format
        # Convert date from unix time to ISO format
        unix_date = datetime.datetime.fromtimestamp(float(prices["date"]))
        prices["date"] = unix_date.strftime("%Y-%m-%d")

        return prices


if __name__ == '__main__':
    # Basic test of Yahoo
    for_date = '2019-02-22'
    ticker = 'spx'
    ticker2 = 'VIG'
    ds = YahooDataSource()
    try:
        d = ds.get_historical_price_data(ticker, "etf", for_date)
        d2 = ds.get_historical_price_data(ticker2, "etf", for_date)
        if d:
            print(ticker)
            print(json.dumps(d, indent=4))
        if d2:
            print(ticker2)
            print(json.dumps(d2, indent=4))
    except Exception as ex:
        print(ex)

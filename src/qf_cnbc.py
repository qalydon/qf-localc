# coding: utf-8
#
# Retrieve data from CNBC
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


class CNBCDataSource(DataSourceBase):
    # Pacing control, hopefully to avoid getting throttled or banned
    # This value is shared across all instances of the data source
    # and NO attempt is made to syncrhonize access to it. The
    # worst outcome is that extra pacing will occur.
    _last_request_time = datetime.datetime.now()
    _pause = float(QConfiguration.qf_cnbc_conf["pacing"]) # float, seconds (e.g. 0.200)

    # Not sure we need the Connection header.
    # The User-Agent header probably makes requests look like they came from a browser
    _headers = {
        'Connection': 'keep-alive',
        'Expires': str(-1),
        'Upgrade-Insecure-Requests': str(1),
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'
    }

    def __init__(self):
        super(CNBCDataSource, self).__init__()
        self.last_payload = None

    def get_historical_price_data(self, symbol, category, for_date):
        """
        CNBC does not provide this service
        :param symbol: ticker symbol
        :param category: not used
        :param for_date: yyyy-mm-dd ISO format
        :return: dict of OHLCV results
        """

        return {}

    def get_dividend_data(self, symbol, for_date, period):
        """
        Essentially a page scrape of a CNBC page containing current data.
        It only works for the current date (trailing 12 months from today).
        This really works only if caching works - it depends on caching to
        supply historical dividends.
        :param symbol: ticker symbol
        :param for_date: yyyy-mm-dd ISO format, must be within 30 days of today.
        :param period: ignored, only 1y supported
        :return: dict of dividend records for period
        """
        # Range check
        fd = datetime.datetime.strptime(for_date, "%Y-%m-%d")
        delta = datetime.datetime.now() - fd
        if delta.days > 30:
            raise ValueError("CNBC only supports TTM dividends based on the most recent 30 days")

        url = "https://www.cnbc.com/quotes/?symbol={}"
        url = url.format(symbol)
        req = urllib.request.Request(url, headers=CNBCDataSource._headers)
        logger.debug("Calling %s", url)

        # Apply pacing, avoid getting throttled
        elapsed = datetime.datetime.now() - CNBCDataSource._last_request_time
        if elapsed.total_seconds() < CNBCDataSource._pause:
            time.sleep(CNBCDataSource._pause)
            logger.debug("Pacing %f...", CNBCDataSource._pause)
        CNBCDataSource._last_request_time = datetime.datetime.now()

        # Send the request and read the response
        try:
            with urllib.request.urlopen(req) as page_source:
                resp = page_source.read().decode()
        except Exception as ex:
            logger.error(ex)
            raise ex

        # Test code
        # with open("qf_cnbc_vym.html", "r") as page_source:
        #     resp = page_source.read()

        # This page scraping technique is highly subject to breakage. It is likely
        # that changes will be required at the least expected time :-)
        # Here is some regex magic. It finds the JSON data in the middle of the web page.
        ptrn = r'.+var\s+symbolInfo\s+\=\s+(\{.+?\}+?);+?.*$'
        try:
            s = re.search(ptrn, resp, re.DOTALL)
            self.last_payload = s.group(1)
            j = json.loads(self.last_payload)
            data = j['FundamentalData']
        except Exception as ex:
            logger.error(ex)
            msg = 'No data fetched for symbol {} using {}'
            raise ValueError(msg.format(symbol, "CNBC"))

        # Select all dividend records
        dividends = [{"amount": data["dividend"]}]
        return dividends


if __name__ == '__main__':
    # Basic test of CNBC
    for_date = datetime.datetime.now().strftime("%Y-%m-%d")
    ticker = 'VYM'
    ds = CNBCDataSource()
    try:
        d = ds.get_dividend_data(ticker, for_date, "1y")
        if d:
            print("TTM Dividend")
            print(ticker)
            print(json.dumps(d, indent=4))
            # Dump the last data payload
            print("Payload")
            j = json.loads(ds.last_payload)
            print(json.dumps(j, indent=2))
    except Exception as ex:
        print(ex)

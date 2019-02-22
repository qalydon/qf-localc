# coding: utf-8
#
# qf_hist_quote - implement historical quote with different data sources
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
from qf_extn_helper import normalize_date
from qf_cache_db import CacheDB
from qf_data_source_mgr import DataSourceMgr
import json

# Logger init
the_app_logger = AppLogger("qf-extension")
logger = the_app_logger.getAppLogger()


def __get_price_record(ticker, category, for_date):
    """
    Return the full cache record for given symbol, date
    :param ticker: Equity ticker symbol
    :param category: Required for WSJ. Not used with Stooq
    :param for_date: Either ISO format or LibreOffice date as a float
    :return: The cache record as a dict
    """
    # Normalize date
    for_date = normalize_date(for_date)

    # Cache look up
    ticker = ticker.upper()
    cr = CacheDB.lookup_closing_price_by_date(ticker, for_date)
    if cr:
        logger.debug("Cache hit for %s %s", ticker, for_date)
        # Turn row into a dict
        r = {}
        for key in cr.keys():
            r[key.lower()] = cr[key]
        return r

    # Try data source
    r = DataSourceMgr.qf_data_source_obj.get_historical_price_data(ticker, category, for_date)
    if r:
        # Verbose debugging
        logger.debug(json.dumps(r))
        # Cache result
        CacheDB.insert_ohlc_price(ticker, for_date,
                                  r["open"], r["high"], r["low"], r["close"], r["volume"],
                                  0.0, DataSourceMgr.data_source())
        return r

    return None


def __get_price(ticker, category, for_date, price_type):
    """

    :param ticker: Equity ticker symbol
    :param category: Required for WSJ. Not used with Stooq
    :param for_date: Either ISO format or LibreOffice date as a float
    :param price_type: open, close, high, low
    :return: The closing price for the given date
    """
    try:
        r = __get_price_record(ticker, category, for_date)
        if r:
            return r[price_type]
    except Exception as ex:
        return str(ex)

    return "N/A"


def closing_price(ticker, category, for_date):
    """

    :param ticker: Equity ticker symbol
    :param category: Required for WSJ. Not used with Stooq
    :param for_date: Either ISO format or LibreOffice date as a float
    :return: The closing price for the given date
    """
    return __get_price(ticker, category, for_date, "close")


def opening_price(ticker, category, for_date):
    """

    :param ticker: Equity ticker symbol
    :param category: Required for WSJ. Not used with Stooq
    :param for_date: Either ISO format or LibreOffice date as a float
    :return: The closing price for the given date
    """
    return __get_price(ticker, category, for_date, "open")


def high_price(ticker, category, for_date):
    """

    :param ticker: Equity ticker symbol
    :param category: Required for WSJ. Not used with Stooq
    :param for_date: Either ISO format or LibreOffice date as a float
    :return: The closing price for the given date
    """
    return __get_price(ticker, category, for_date, "high")


def low_price(ticker, category, for_date):
    """

    :param ticker: Equity ticker symbol
    :param category: Required for WSJ. Not used with Stooq
    :param for_date: Either ISO format or LibreOffice date as a float
    :return: The closing price for the given date
    """
    return __get_price(ticker, category, for_date, "low")


def daily_volume(ticker, category, for_date):
    """

    :param ticker: Equity ticker symbol
    :param category: Required for WSJ. Not used with Stooq
    :param for_date: Either ISO format or LibreOffice date as a float
    :return: The closing price for the given date
    """
    return __get_price(ticker, category, for_date, "volume")

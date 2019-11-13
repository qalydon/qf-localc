# coding: utf-8
#
# qf_dividends - implement dividends with different data sources
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
from qf_configuration import QConfiguration
import json

# Logger init
the_app_logger = AppLogger("qf-extension")
logger = the_app_logger.getAppLogger()


def _get_ttm_dividend_record(ticker, for_date):
    """
    Return the full cache record for given symbol, date
    :param ticker: Equity ticker symbol
    :param for_date: Either ISO format or LibreOffice date as a float
    :return: The cache record as a dict
    """
    # Normalize date
    for_date = normalize_date(for_date)

    # Cache look up
    ticker = ticker.upper()
    cr = CacheDB.lookup_ttm_dividend_by_date(ticker, for_date)
    if cr:
        logger.debug("Cache hit for %s %s", ticker, for_date)
        # Turn row into a dict
        r = {}
        for key in cr.keys():
            r[key.lower()] = cr[key]
        return r

    # Try data sources for dividends
    data_source_list = QConfiguration.get_datasources_list("dividend")
    for dsn in data_source_list:
        try:
            # Get distributions for previous 12 months from given date
            r = DataSourceMgr.get_data_source(dsn).get_dividend_data(ticker, for_date, "1y")
            if r:
                # Verbose debugging
                logger.debug(json.dumps(r))
                # Sum distributions
                dividend = 0.0
                for dist in r:
                    dividend += float(dist["amount"])
                # Create ttm dividend dict as the result
                res = {}
                res["symbol"] = ticker
                res["calcdate"] = for_date
                res["amount"] = dividend
                res["source"] = dsn
                # Cache result
                CacheDB.insert_ttm_dividend(ticker, for_date, dividend, dsn)
                return res
        except Exception as ex:
            logger.error("Exception %s", ex)
            logger.error(str(ex))

    logger.error("No data source for dividend returned a result")
    return None

def ttm_dividend(ticker, for_date):
    """
    Return the trailing 12 month dividend for a given date
    :param ticker: ticker symbol
    :param for_date: Either ISO format or LibreOffice date as a float
    :return: the dividend amount
    """
    try:
        r = _get_ttm_dividend_record(ticker, for_date)
        if r:
            return r["amount"]
    except Exception as ex:
        return str(ex)

    return "N/A"

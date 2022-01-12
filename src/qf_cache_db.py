# coding: utf-8
#
# cache_db - Implements the persistent cache
# Copyright © 2018, 2022  Dave Hocker (email: Qalydon17@gmail.com)
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
from qf_configuration import QConfiguration
from qf_csv_cache_file import QFCSVCacheFile
import os

# Logger init
the_app_logger = AppLogger("qf-extension")
logger = the_app_logger.getAppLogger()


class CacheDB:
    """
    Implements a data caching scheme using CSV files. Originally, the caching
    scheme was based on Sqlite3, but LibreOffice dropped Sqlite3 from its embedded
    Python package. As a result, caching is now performed using CSV files.
    """

    # Singleton instances of CSV cache files
    price_cache = None
    dividend_cache = None

    PRICE_CACHE_KEYS = ['Open', 'High', 'Low', 'Close', 'Volume', 'Adj_Close']
    DIVIDEND_CACHE_KEYS = ['Amount']

    @classmethod
    def _open_price_cache(cls):
        # Determine cache location based on underlying OS
        # TODO Replace/remove DB from configuration
        full_file_path = QConfiguration.qf_cache_db
        file_path = os.path.dirname(full_file_path)

        # Make the folder if it does not exist
        if not os.path.exists(file_path):
            logger.info("Create directory")
            os.makedirs(file_path)
        full_file_path = os.path.join(file_path, "symbol_date.csv")

        if cls.price_cache is None:
            logger.debug("Opening price cache file %s", full_file_path)
            cls.price_cache = QFCSVCacheFile(full_file_path,
                                         symbol="Symbol", value_date="Date",
                                         value_keys=cls.PRICE_CACHE_KEYS)
            # Create the CSV file if it does not exist
            if not os.path.exists(full_file_path):
                cls.price_cache.create_csv()
                logger.debug("Created %s", full_file_path)
            cls.price_cache.load_csv()

        return cls.price_cache

    @classmethod
    def _open_dividend_cache(cls):
        # Determine cache location based on underlying OS
        # TODO Replace/remove DB from configuration
        full_file_path = QConfiguration.qf_cache_db
        file_path = os.path.dirname(full_file_path)

        # Make the folder if it does not exist
        if not os.path.exists(file_path):
            logger.info("Create directory")
            os.makedirs(file_path)
        full_file_path = os.path.join(file_path, "ttmdividends.csv")

        if cls.dividend_cache is None:
            logger.debug("Opening dividend cache file %s", full_file_path)
            cls.dividend_cache = QFCSVCacheFile(full_file_path,
                                         symbol="Symbol", value_date="CalcDate",
                                         value_keys=cls.DIVIDEND_CACHE_KEYS)
            # If the CSV file does not exist, create it
            if not os.path.exists(full_file_path):
                cls.dividend_cache.create_csv()
                logger.debug("Created %s", full_file_path)
            cls.dividend_cache.load_csv()

        return cls.dividend_cache

    @classmethod
    def lookup_closing_price_by_date(cls, symbol, tgtdate):
        """
        Look up cached historical data for a given symbol/date pair.
        :param symbol:
        :param tgtdate:
        :return: Returns the cached DB record. If no record is found, returns None.
        """
        cache_file = cls._open_price_cache()
        r = cache_file.get_cache_record(symbol, tgtdate)
        # r will be None if no record was found
        return r

    @classmethod
    def insert_closing_price(cls, symbol, tgtdate, close, data_source):
        """
        Insert a new cache record in the cache DB.
        :param symbol:
        :param tgtdate:
        :param close:
        :param data_source: text
        :return:
        """
        cache_file = cls._open_price_cache()
        values = {}
        for k in cls.PRICE_CACHE_KEYS:
            values[k] = 0
        values["Close"] = close
        cache_file.add_cache_record(symbol, tgtdate, values)

    @classmethod
    def insert_ohlc_price(cls, symbol, tgtdate, open_price, high_price, low_price, closing_price, volume, adj_closing_price, data_source):
        """
        Insert an OHLC record into the cache DB. Missing values should be 0.0 or 0.
        :param symbol:
        :param tgtdate: yyyy-mm-dd
        :param open_price: float
        :param high_price: float
        :param low_price: float
        :param closing_price: float
        :param volume: integer
        :param adj_closing_price: float
        :param data_source: text
        :return: None
        """
        cache_file = cls._open_price_cache()
        values = {
            "Open": open_price,
            "High": high_price,
            "Low": low_price,
            "Close": closing_price,
            "Volume": volume,
            "Adj_Close": adj_closing_price
        }
        cache_file.add_cache_record(symbol, tgtdate, values)

    @classmethod
    def lookup_ttm_dividend_by_date(cls, symbol, tgtdate):
        """
        Look up cached historical data for a given symbol/date pair.
        :param symbol:
        :param tgtdate:
        :return: Returns the cached DB record. If no record is found, returns None.
        """
        cache_file = cls._open_dividend_cache()
        r = cache_file.get_cache_record(symbol, tgtdate)
        return r

    @classmethod
    def insert_ttm_dividend(cls, symbol, tgtdate, dividend, source):
        """
        Insert a new cache record in the cache DB. The Google service does not
        produce all data values for every symbol (e.g. mutual funds only have closing prices).
        to preserve backward compatiblity in the cache DB zero values are used for unavailable values.
        :param symbol:
        :param tgtdate:
        :param close:
        :return:
        """
        cache_file = cls._open_dividend_cache()
        values = {"Amount": dividend}
        cache_file.add_cache_record(symbol, tgtdate, values)

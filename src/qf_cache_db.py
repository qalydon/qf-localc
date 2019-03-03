# coding: utf-8
#
# cache_db - Implements the persistent cache as a database
# Copyright (C) 2018  Dave Hocker (email: Qalydon17@gmail.com)
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
import sqlite3
import os

# Logger init
the_app_logger = AppLogger("qf-extension")
logger = the_app_logger.getAppLogger()


class CacheDB:
    @classmethod
    def __open_yh_cache(cls):
        """
        Open a connection to the cache DB. Create the DB if it does not exist.
        :return: Database connection.
        """
        # Determine cache location based on underlying OS
        full_file_path = QConfiguration.qf_cache_db
        file_path = os.path.dirname(full_file_path)

        # Make the folder if it does not exist
        if not os.path.exists(file_path):
            logger.info("Create directory")
            os.makedirs(file_path)

        # If DB does not exist, create it
        # TODO Move this out to its own function. Consider putting
        # initialization SQL in a text file.
        if not os.path.exists(full_file_path):
            logger.info("Create database")
            conn = sqlite3.connect(full_file_path)
            conn.execute("CREATE TABLE SymbolDate (Symbol text not null, Date text not null, Open real, High real, Low real, Close real, Volume integer, Adj_Close real, Source text, PRIMARY KEY(Symbol,Date))")
            conn.execute("CREATE TABLE TTMDividends (Symbol TEXT NOT NULL, CalcDate TEXT NOT NULL, Amount REAL NOT NULL, Source TEXT, PRIMARY KEY(Symbol,CalcDate))")
        else:
            conn = sqlite3.connect(full_file_path)

        # We use the row factory to get named row columns. Makes handling row sets easier.
        conn.row_factory = sqlite3.Row
        # The default string type is unicode. This changes it to UTF-8.
        conn.text_factory = str

        # return connection to the cache DB
        return conn

    @classmethod
    def lookup_closing_price_by_date(cls, symbol, tgtdate):
        """
        Look up cached historical data for a given symbol/date pair.
        :param symbol:
        :param tgtdate:
        :return: Returns the cached DB record. If no record is found, returns None.
        """
        conn = cls.__open_yh_cache()
        rset = conn.execute("SELECT * from SymbolDate where Symbol=? and Date=?", [symbol, tgtdate])
        r = rset.fetchone()
        conn.close()
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
        conn = cls.__open_yh_cache()
        # print ("Cache data:", symbol, tgtdate, close)
        conn.execute("INSERT INTO SymbolDate values (?,?,?,?,?,?,?,?,?)", [symbol, tgtdate, 0, 0, 0, close, 0, 0, data_source])
        conn.commit()
        conn.close()

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
        conn = cls.__open_yh_cache()
        # print ("Cache data:", symbol, tgtdate, close)
        conn.execute("INSERT INTO SymbolDate values (?,?,?,?,?,?,?,?,?)",
                     [symbol, tgtdate, open_price, high_price, low_price, closing_price, volume, adj_closing_price, data_source])
        conn.commit()
        conn.close()

    @classmethod
    def lookup_ttm_dividend_by_date(cls, symbol, tgtdate):
        """
        Look up cached historical data for a given symbol/date pair.
        :param symbol:
        :param tgtdate:
        :return: Returns the cached DB record. If no record is found, returns None.
        """
        conn = cls.__open_yh_cache()
        rset = conn.execute("SELECT * from TTMDividends where Symbol=? and CalcDate=?", [symbol, tgtdate])
        r = rset.fetchone()
        conn.close()
        # r will be None if no record was found
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
        conn = cls.__open_yh_cache()
        conn.execute("INSERT INTO TTMdividends values (?,?,?,?)", [symbol, tgtdate, dividend, source])
        conn.commit()
        conn.close()
